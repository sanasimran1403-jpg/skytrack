import random

from app.algo.geo import haversine_km
from app.algo.spatial_index import GridIndex, brute_force_radius


def test_haversine_same_point_is_zero():
    assert haversine_km(17.4, 78.4, 17.4, 78.4) == 0


def test_haversine_known_distance():
    # Hyderabad to Bengaluru is roughly 500 km
    d = haversine_km(17.3850, 78.4867, 12.9716, 77.5946)
    assert 490 < d < 510


def test_grid_matches_brute_force():
    random.seed(42)
    points = [
        (i, random.uniform(12, 21), random.uniform(74, 83)) for i in range(2000)
    ]
    grid = GridIndex(cell_deg=0.5)
    for item_id, lat, lon in points:
        grid.insert(item_id, lat, lon)

    for _ in range(50):
        lat = random.uniform(12, 21)
        lon = random.uniform(74, 83)
        radius = random.uniform(10, 200)
        assert grid.query_radius(lat, lon, radius) == brute_force_radius(
            points, lat, lon, radius
        )