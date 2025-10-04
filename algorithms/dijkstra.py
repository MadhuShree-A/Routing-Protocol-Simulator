import heapq

def dijkstra(num_nodes, edges, source):
    graph = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))  # undirected

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
        next_hop = dest
        while prev[next_hop] != source and prev[next_hop] is not None:
            next_hop = prev[next_hop]
        routing_table.append({
            "Destination": dest,
            "NextHop": next_hop if prev[dest] is not None else "-",
            "Cost": dist[dest]
        })
    return routing_table
