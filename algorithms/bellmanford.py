def bellman_ford(num_nodes, edges, source):
    """
    Bellman-Ford Algorithm (works with negative weights).
    Detects negative cycles. Builds routing table (distance-vector style).
    """

    # Build neighbor list (undirected graph)
    neighbors = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        neighbors[u].append((v, w))
        neighbors[v].append((u, w))

    # Initialize
    dist = [float('inf')] * num_nodes
    prev = [None] * num_nodes
    dist[source] = 0

 
    for _ in range(num_nodes - 1):
        updated = False
        for u in range(num_nodes):
            if dist[u] == float('inf'):
                continue
            for v, w in neighbors[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    updated = True
        if not updated:
            break


    for u in range(num_nodes):
        if dist[u] == float('inf'):
            continue
        for v, w in neighbors[u]:
            if dist[u] + w < dist[v]:
                return {"error": "Negative weight cycle detected"}


    routing_table = []
    for dest in range(num_nodes):
        if dest == source:
            continue

        if dist[dest] == float('inf'):
            routing_table.append({"Destination": dest, "NextHop": "-", "Cost": "∞"})
            continue

        # trace next hop
        next_hop = dest
        while prev[next_hop] is not None and prev[next_hop] != source:
            next_hop = prev[next_hop]

        routing_table.append({
            "Destination": dest,
            "NextHop": next_hop if prev[next_hop] is not None else dest,
            "Cost": dist[dest]
        })

    return routing_table
