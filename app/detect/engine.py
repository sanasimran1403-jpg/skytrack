from app.algo.sliding_window import SlidingWindow
from app.detect.spoof_check import check_jump
from app.detect.squawk import check_squawk

DESCENT_WINDOW_S = 120
DESCENT_DROP_M = 4000  # ~33 m/s sustained, far steeper than a normal descent


def detect(readings):
    """Run all detectors over readings (dicts with icao24, ts, lat, lon,
    altitude_m, squawk). Each aircraft's readings must be in time order.
    Returns a list of alert dicts: icao24, type, ts, details.
    """
    prev = {}
    windows = {}
    alerts = []

    for r in readings:
        icao = r["icao24"]

        alert = check_squawk(r)
        if alert:
            alerts.append(alert)

        p = prev.get(icao)
        if p is not None:
            alert = check_jump(p, r)
            if alert:
                alerts.append(alert)
        prev[icao] = r

        alt = r.get("altitude_m")
        if alt is not None:
            w = windows.setdefault(icao, SlidingWindow(DESCENT_WINDOW_S))
            w.add(r["ts"], alt)
            old_ts, old_alt = w.oldest()
            if old_ts < r["ts"] and old_alt - alt > DESCENT_DROP_M:
                alerts.append({
                    "icao24": icao,
                    "type": "rapid_descent",
                    "ts": r["ts"],
                    "details": f"dropped {old_alt - alt:.0f} m within "
                               f"{(r['ts'] - old_ts).total_seconds():.0f} s",
                })

    return alerts