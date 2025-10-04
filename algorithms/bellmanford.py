def bellman_ford(num_nodes, edges, source):
    # Build neighbor list
    neighbors = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        neighbors[u].append((v, w))
        neighbors[v].append((u, w))

    # Initialize distances for this source
    dist = [float('inf')] * num_nodes
    prev = [None] * num_nodes
    dist[source] = 0

    # Distance Vector iterative update
    updated = True
    while updated:
        updated = False
        for u in range(num_nodes):
            for v, w in neighbors[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    updated = True

    # Build routing table
    routing_table = []
    for dest in range(num_nodes):
        if dest == source: 
            continue
        next_hop = dest
        while prev[next_hop] != source and prev[next_hop] is not None:
            next_hop = prev[next_hop]
        routing_table.append({
            "Destination": dest,
            "NextHop": next_hop if prev[dest] is not None else "-",
            "Cost": dist[dest]
        })

    return routing_table
