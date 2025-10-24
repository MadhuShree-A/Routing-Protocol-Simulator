from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, abort
import io, csv, json
from algorithms.dijkstra import dijkstra
from algorithms.bellmanford import bellman_ford

app = Flask(__name__)
app.secret_key = "secret123"   # needed for session storage

@app.route("/")
def welcome():
    return redirect(url_for("intro"))

@app.route("/intro")
def intro():
    return render_template("intro.html")

@app.route("/topology")
def index():
    return render_template("topology.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    """
    Expects JSON:
    {
      "nodes": [...],
      "edges": [...],
      "algorithm": "dijkstra" | "bellmanford" | "both"
    }
    """
    data = request.json or {}
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    algorithm = data.get("algorithm", "both")

    # Normalize edge tuple list: (u, v, weight)
    edge_list = []
    for e in edges:
        try:
            u = int(e["from"])
            v = int(e["to"])
            w = float(e.get("weight", 1))
        except Exception:
            return jsonify({"error": "Invalid edge format"}), 400
        edge_list.append((u, v, w))

    # Validate weights for Dijkstra (must be non-negative)
    if algorithm in ("dijkstra", "both"):
        has_negative = any(w < 0 for (_, _, w) in edge_list)
        if has_negative:
            return jsonify({
                "error": "Dijkstra requires non-negative weights. Detected negative weight(s)."
            }), 422

    num_nodes = len(nodes)

    ls_tables = {}
    dv_tables = {}

    if algorithm in ("dijkstra", "both"):
        # run Dijkstra for each node as source
        for node in range(num_nodes):
            ls_tables[node] = dijkstra(num_nodes, edge_list, node)

    if algorithm in ("bellmanford", "both"):
        for node in range(num_nodes):
            dv_tables[node] = bellman_ford(num_nodes, edge_list, node)

    # Save minimal topology to session for visualization/export
    session["topo_nodes"] = nodes
    session["topo_edges"] = edges
    session["ls_tables"] = ls_tables
    session["dv_tables"] = dv_tables
    session["last_algorithm"] = algorithm

    return jsonify({"redirect": url_for("results")})

@app.route("/results")
def results():
    ls_tables = session.get("ls_tables", {})
    dv_tables = session.get("dv_tables", {})
    algorithm = session.get("last_algorithm", "both")
    return render_template("results.html", ls=ls_tables, dv=dv_tables, algorithm=algorithm)

@app.route("/visualize")
def visualize():
    # Visualization uses session-stored topology + tables
    nodes = session.get("topo_nodes", [])
    edges = session.get("topo_edges", [])
    ls_tables = session.get("ls_tables", {})
    dv_tables = session.get("dv_tables", {})
    algorithm = session.get("last_algorithm", "both")
    return render_template("visualize.html", nodes=nodes, edges=edges, ls=ls_tables, dv=dv_tables, algorithm=algorithm)

def _tables_to_csv_bytes(tables, title="routing"):
    # tables: {source: [ {Destination, NextHop, Cost}, ... ] }
    buf = io.StringIO()
    writer = csv.writer(buf)
    # Write a simple CSV that groups by source
    for src, rows in tables.items():
        writer.writerow([f"Source,R{src}"])
        writer.writerow(["Destination","NextHop","Cost"])
        for r in rows:
            writer.writerow([r.get("Destination"), r.get("NextHop"), r.get("Cost")])
        writer.writerow([])  # blank line between sources
    return buf.getvalue().encode("utf-8")

@app.route("/export/<alg>")
def export(alg):
    alg = alg.lower()
    if alg not in ("dijkstra", "bellmanford", "both"):
        abort(404)
    filename = f"routing_{alg}.csv"
    if alg == "dijkstra":
        tables = session.get("ls_tables", {})
    elif alg == "bellmanford":
        tables = session.get("dv_tables", {})
    else:
        # both: combine
        combined = {}
        combined.update({"LS_Source_"+str(k): v for k,v in session.get("ls_tables", {}).items()})
        combined.update({"DV_Source_"+str(k): v for k,v in session.get("dv_tables", {}).items()})
        # Convert keys to integers not required — produce CSV of the combined dict
        buf = io.StringIO()
        writer = csv.writer(buf)
        for key, rows in combined.items():
            writer.writerow([f"{key}"])
            writer.writerow(["Destination","NextHop","Cost"])
            for r in rows:
                writer.writerow([r.get("Destination"), r.get("NextHop"), r.get("Cost")])
            writer.writerow([])
        data = buf.getvalue().encode("utf-8")
        return send_file(io.BytesIO(data), as_attachment=True, download_name=filename, mimetype="text/csv")

    data = _tables_to_csv_bytes(tables)
    return send_file(io.BytesIO(data), as_attachment=True, download_name=filename, mimetype="text/csv")

@app.route("/export_json")
def export_json():
    out = {
        "nodes": session.get("topo_nodes", []),
        "edges": session.get("topo_edges", []),
        "ls_tables": session.get("ls_tables", {}),
        "dv_tables": session.get("dv_tables", {})
    }
    data = json.dumps(out, indent=2)
    return send_file(io.BytesIO(data.encode("utf-8")), as_attachment=True, download_name="routing.json", mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
