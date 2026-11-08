import math
import random

import pytest

from app.algo.geo import haversine_km
from app.algo.graph import AIRPORTS, astar, build_graph, dijkstra
from app.algo.heap import MinHeap, n_nearest


def test_heap_pops_in_sorted_order():
    random.seed(7)
    values = [random.randint(0, 1000) for _ in range(500)]
    heap = MinHeap()
    for v in values:
        heap.push(v)
    assert [heap.pop() for _ in range(len(values))] == sorted(values)


def test_heap_empty_raises():
    with pytest.raises(IndexError):
        MinHeap().pop()


def test_n_nearest_matches_sorting():
    random.seed(3)
    points = [(i, random.uniform(12, 21), random.uniform(74, 83)) for i in range(1000)]
    lat, lon = 17.4, 78.4
    expected = sorted(
        (haversine_km(lat, lon, plat, plon), i) for i, plat, plon in points
    )[:5]
    assert n_nearest(points, lat, lon, 5) == expected


def test_dijkstra_path_is_valid():
    graph = build_graph(AIRPORTS, max_leg_km=800)
    dist, path, _ = dijkstra(graph, "DEL", "MAA")
    assert path[0] == "DEL" and path[-1] == "MAA"
    total = 0.0
    for a, b in zip(path, path[1:]):
        weights = dict(graph[a])
        assert b in weights  # every hop is a real edge
        total += weights[b]
    assert math.isclose(total, dist)


def test_astar_matches_dijkstra_for_all_pairs():
    graph = build_graph(AIRPORTS, max_leg_km=800)
    for a in AIRPORTS:
        for b in AIRPORTS:
            d1, _, _ = dijkstra(graph, a, b)
            d2, _, _ = astar(graph, AIRPORTS, a, b)
            assert math.isclose(d1, d2)


def test_unreachable_returns_inf():
    graph = build_graph(AIRPORTS, max_leg_km=50)  # almost no edges
    dist, path, _ = dijkstra(graph, "DEL", "MAA")
    assert dist == math.inf and path == []