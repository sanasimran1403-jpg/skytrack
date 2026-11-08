import math
from collections import defaultdict

from app.algo.geo import haversine_km

KM_PER_DEG_LAT = 111.32


class GridIndex:
    """Uniform lat/lon grid.

    insert: O(1)
    query_radius: O(k + m) where k = cells touched, m = points inside them
    (vs O(n) for brute force). Does not handle longitude wrap-around at
    +/-180 degrees (fine for a regional dataset like India).
    """

    def __init__(self, cell_deg=0.5):
        self.cell_deg = cell_deg
        self.cells = defaultdict(list)  # (row, col) -> [(item_id, lat, lon)]
        self.size = 0

    def _cell(self, lat, lon):
        return (math.floor(lat / self.cell_deg), math.floor(lon / self.cell_deg))

    def insert(self, item_id, lat, lon):
        self.cells[self._cell(lat, lon)].append((item_id, lat, lon))
        self.size += 1

    def query_radius(self, lat, lon, radius_km):
        """Return [(distance_km, item_id), ...] within radius, nearest first."""
        dlat = radius_km / KM_PER_DEG_LAT
        cos_lat = max(math.cos(math.radians(lat)), 0.01)
        dlon = radius_km / (KM_PER_DEG_LAT * cos_lat)

        r_min, c_min = self._cell(lat - dlat, lon - dlon)
        r_max, c_max = self._cell(lat + dlat, lon + dlon)

        found = []
        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                for item_id, plat, plon in self.cells.get((r, c), ()):
                    d = haversine_km(lat, lon, plat, plon)
                    if d <= radius_km:
                        found.append((d, item_id))
        found.sort()
        return found


def brute_force_radius(points, lat, lon, radius_km):
    """Reference implementation, O(n). points = [(item_id, lat, lon), ...]"""
    out = []
    for item_id, plat, plon in points:
        d = haversine_km(lat, lon, plat, plon)
        if d <= radius_km:
            out.append((d, item_id))
    out.sort()
    return out