import heapq

def dijkstra(num_nodes, edges, source):
    """
    edges: list of (u, v, w)
    returns: routing table list of dicts: {Destination, NextHop, Cost}
    Dijkstra requires non-negative weights. This function assumes validation is done upstream.
    """
    graph = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))  # undirected graph assumption

    dist = {i: float('inf') for i in range(num_nodes)}
    prev = {i: None for i in range(num_nodes)}
    dist[source] = 0
    pq = [(0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))

    routing_table = []
    for dest in range(num_nodes):
        if dest == source:
            continue
        if prev[dest] is None and dist[dest] == float('inf'):
            routing_table.append({"Destination": dest, "NextHop": "-", "Cost": "∞"})
            continue
        # backtrack to find next hop
        next_hop = dest
        while prev[next_hop] is not None and prev[next_hop] != source:
            next_hop = prev[next_hop]
        if prev[next_hop] is None and next_hop != source and prev[next_hop] is None and next_hop == dest and prev[dest] is None:
            # unreachable from source
            routing_table.append({"Destination": dest, "NextHop": "-", "Cost": "∞"})
        else:
            nh = next_hop if prev[next_hop] is not None or next_hop == source or next_hop != dest else next_hop
            routing_table.append({"Destination": dest, "NextHop": nh if nh != source else dest, "Cost": dist[dest]})
    return routing_table
