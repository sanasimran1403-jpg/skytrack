from app.algo.geo import haversine_km

MAX_PLAUSIBLE_KMH = 1300  # faster than any civil airliner cruises
MIN_DT_SECONDS = 1


def check_jump(prev, cur, max_kmh=MAX_PLAUSIBLE_KMH):
    """Flag physically impossible movement between two consecutive readings
    of the same aircraft (bad data or spoofed ADS-B position)."""
    dt = (cur["ts"] - prev["ts"]).total_seconds()
    if dt < MIN_DT_SECONDS:
        return None
    if None in (prev["lat"], prev["lon"], cur["lat"], cur["lon"]):
        return None

    km = haversine_km(prev["lat"], prev["lon"], cur["lat"], cur["lon"])
    kmh = km / dt * 3600
    if kmh <= max_kmh:
        return None

    return {
        "icao24": cur["icao24"],
        "type": "position_jump",
        "ts": cur["ts"],
        "details": f"moved {km:.1f} km in {dt:.0f} s (~{kmh:.0f} km/h)",
    }