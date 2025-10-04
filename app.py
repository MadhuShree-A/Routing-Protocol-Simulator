from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from algorithms.dijkstra import dijkstra
from algorithms.bellmanford import bellman_ford

app = Flask(__name__)
app.secret_key = "secret123"   # needed for session storage

@app.route("/")
def index():
    return render_template("topology.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.json
    nodes = data["nodes"]
    edges = data["edges"]

    num_nodes = len(nodes)
    edge_list = [(e["from"], e["to"], e["weight"]) for e in edges]

    # Generate both LS & DV tables
    ls_tables = {}
    dv_tables = {}
    for node in range(num_nodes):
        ls_tables[node] = dijkstra(num_nodes, edge_list, node)
        dv_tables[node] = bellman_ford(num_nodes, edge_list, node)

    # Store results in session and redirect
    session["ls_tables"] = ls_tables
    session["dv_tables"] = dv_tables
    return jsonify({"redirect": url_for("results")})


@app.route("/results")
def results():
    ls_tables = session.get("ls_tables", {})
    dv_tables = session.get("dv_tables", {})
    return render_template("results.html", ls=ls_tables, dv=dv_tables)
    

if __name__ == "__main__":
    app.run(debug=True)
