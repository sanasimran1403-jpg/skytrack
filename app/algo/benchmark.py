import random
import time

from app.algo.spatial_index import GridIndex, brute_force_radius

N_POINTS = 20_000
N_QUERIES = 100
RADIUS_KM = 50

random.seed(1)
points = [(i, random.uniform(12, 21), random.uniform(74, 83)) for i in range(N_POINTS)]
queries = [(random.uniform(12, 21), random.uniform(74, 83)) for _ in range(N_QUERIES)]

grid = GridIndex(cell_deg=0.5)
t0 = time.perf_counter()
for item_id, lat, lon in points:
    grid.insert(item_id, lat, lon)
build = time.perf_counter() - t0

t0 = time.perf_counter()
for lat, lon in queries:
    grid.query_radius(lat, lon, RADIUS_KM)
grid_time = time.perf_counter() - t0

t0 = time.perf_counter()
for lat, lon in queries:
    brute_force_radius(points, lat, lon, RADIUS_KM)
brute_time = time.perf_counter() - t0

print(f"points={N_POINTS}, queries={N_QUERIES}, radius={RADIUS_KM} km")
print(f"grid build : {build:.3f} s")
print(f"grid query : {grid_time:.3f} s")
print(f"brute force: {brute_time:.3f} s")
print(f"speedup    : {brute_time / grid_time:.1f}x")