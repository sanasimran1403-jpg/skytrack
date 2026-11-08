from datetime import datetime, timedelta, timezone

from app.algo.sliding_window import SlidingWindow
from app.detect.engine import detect

T0 = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)


def reading(icao24, sec, lat=17.0, lon=78.0, alt=10000.0, squawk=None):
    return {
        "icao24": icao24,
        "ts": T0 + timedelta(seconds=sec),
        "lat": lat,
        "lon": lon,
        "altitude_m": alt,
        "squawk": squawk,
    }


def types(alerts):
    return [a["type"] for a in alerts]


def test_sliding_window_evicts_and_averages():
    w = SlidingWindow(60)
    w.add(T0, 10)
    w.add(T0 + timedelta(seconds=30), 20)
    assert w.average() == 15
    w.add(T0 + timedelta(seconds=100), 30)
    assert len(w) == 1
    assert w.average() == 30


def test_emergency_squawk_detected():
    assert types(detect([reading("a1", 0, squawk="7700")])) == ["emergency_squawk"]


def test_normal_squawk_ignored():
    assert detect([reading("a1", 0, squawk="1200")]) == []


def test_impossible_jump_detected():
    # ~111 km in 60 s = ~6600 km/h
    alerts = detect([reading("a1", 0, lat=17.0), reading("a1", 60, lat=18.0)])
    assert types(alerts) == ["position_jump"]


def test_normal_movement_ignored():
    # ~11 km in 60 s = ~670 km/h
    alerts = detect([reading("a1", 0, lat=17.0), reading("a1", 60, lat=17.1)])
    assert alerts == []


def test_rapid_descent_detected():
    alerts = detect([reading("a1", 0, alt=10000), reading("a1", 60, alt=5000)])
    assert types(alerts) == ["rapid_descent"]


def test_normal_descent_ignored():
    alerts = detect([reading("a1", 0, alt=10000), reading("a1", 60, alt=9500)])
    assert alerts == []


def test_aircraft_are_tracked_independently():
    alerts = detect([
        reading("a1", 0, lat=17.0),
        reading("b2", 30, lat=25.0),  # different aircraft, far away: not a jump
        reading("a1", 60, lat=17.1),
    ])
    assert alerts == []