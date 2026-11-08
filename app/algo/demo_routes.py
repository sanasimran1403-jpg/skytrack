from app.algo.graph import AIRPORTS, astar, build_graph, dijkstra

graph = build_graph(AIRPORTS, max_leg_km=800)
edges = sum(len(v) for v in graph.values()) // 2
print(f"airports: {len(graph)}, routes: {edges}\n")

for start, goal in [("DEL", "MAA"), ("TRV", "CCU"), ("JAI", "HYD")]:
    d1, p1, e1 = dijkstra(graph, start, goal)
    d2, p2, e2 = astar(graph, AIRPORTS, start, goal)
    print(f"{start} -> {goal}")
    print(f"  Dijkstra: {d1:7.1f} km  {' > '.join(p1)}  (expanded {e1})")
    print(f"  A*      : {d2:7.1f} km  {' > '.join(p2)}  (expanded {e2})\n")