import math

from app.algo.geo import haversine_km
from app.algo.heap import MinHeap

# code -> (name, lat, lon). Approximate coordinates.
AIRPORTS = {
    "HYD": ("Hyderabad", 17.2403, 78.4294),
    "BLR": ("Bengaluru", 13.1986, 77.7066),
    "MAA": ("Chennai", 12.9941, 80.1709),
    "BOM": ("Mumbai", 19.0896, 72.8656),
    "DEL": ("Delhi", 28.5562, 77.1000),
    "CCU": ("Kolkata", 22.6547, 88.4467),
    "COK": ("Kochi", 10.1520, 76.4019),
    "GOI": ("Goa", 15.3808, 73.8314),
    "PNQ": ("Pune", 18.5821, 73.9197),
    "AMD": ("Ahmedabad", 23.0772, 72.6347),
    "VTZ": ("Visakhapatnam", 17.7212, 83.2245),
    "TRV": ("Thiruvananthapuram", 8.4821, 76.9201),
    "IXE": ("Mangaluru", 12.9613, 74.8901),
    "CJB": ("Coimbatore", 11.0300, 77.0434),
    "IXM": ("Madurai", 9.8345, 78.0934),
    "TIR": ("Tirupati", 13.6325, 79.5433),
    "VGA": ("Vijayawada", 16.5304, 80.7968),
    "NAG": ("Nagpur", 21.0922, 79.0472),
    "IDR": ("Indore", 22.7218, 75.8011),
    "JAI": ("Jaipur", 26.8242, 75.8122),
}


def build_graph(airports, max_leg_km=800):
    """Adjacency list: code -> [(neighbour_code, distance_km), ...].

    Two airports are connected if they are within max_leg_km of each other
    (models a limited-range regional network, so routes need multiple hops).
    Build time: O(V^2).
    """
    graph = {code: [] for code in airports}
    codes = list(airports)
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            d = haversine_km(
                airports[a][1], airports[a][2], airports[b][1], airports[b][2]
            )
            if d <= max_leg_km:
                graph[a].append((b, d))
                graph[b].append((a, d))
    return graph


def dijkstra(graph, start, goal):
    """Shortest path. Time: O((V + E) log V). Returns (km, path, nodes_expanded)."""
    dist = {start: 0.0}
    prev = {}
    heap = MinHeap()
    heap.push((0.0, start))
    expanded = 0

    while len(heap):
        d, node = heap.pop()
        if d > dist.get(node, math.inf):
            continue  # stale heap entry
        expanded += 1
        if node == goal:
            break
        for nxt, w in graph[node]:
            nd = d + w
            if nd < dist.get(nxt, math.inf):
                dist[nxt] = nd
                prev[nxt] = node
                heap.push((nd, nxt))

    if goal not in dist:
        return math.inf, [], expanded
    return dist[goal], _build_path(prev, start, goal), expanded


def astar(graph, airports, start, goal):
    """A* with a haversine heuristic (admissible and consistent here).

    Same worst case as Dijkstra, but usually expands fewer nodes.
    Returns (km, path, nodes_expanded).
    """
    glat, glon = airports[goal][1], airports[goal][2]

    def h(code):
        return haversine_km(airports[code][1], airports[code][2], glat, glon)

    g = {start: 0.0}
    prev = {}
    closed = set()
    heap = MinHeap()
    heap.push((h(start), start))
    expanded = 0

    while len(heap):
        _, node = heap.pop()
        if node in closed:
            continue
        closed.add(node)
        expanded += 1
        if node == goal:
            break
        for nxt, w in graph[node]:
            ng = g[node] + w
            if ng < g.get(nxt, math.inf):
                g[nxt] = ng
                prev[nxt] = node
                heap.push((ng + h(nxt), nxt))

    if goal not in g:
        return math.inf, [], expanded
    return g[goal], _build_path(prev, start, goal), expanded


def _build_path(prev, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()
    return path