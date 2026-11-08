import os
from collections import Counter

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from app.detect.engine import detect

load_dotenv()

FETCH = text("""
    SELECT icao24, ts, lat, lon, altitude_m, squawk
    FROM positions
    ORDER BY icao24, ts
""")

INSERT_ALERT = text("""
    INSERT INTO alerts (icao24, type, ts, details)
    VALUES (:icao24, :type, :ts, :details)
    ON CONFLICT (icao24, type, ts) DO NOTHING
""")


def main():
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.begin() as conn:
        rows = [dict(r) for r in conn.execute(FETCH).mappings()]
        alerts = detect(rows)
        if alerts:
            conn.execute(INSERT_ALERT, alerts)

    print(f"readings checked: {len(rows)}, alerts found: {len(alerts)}")
    for kind, n in Counter(a["type"] for a in alerts).items():
        print(f"  {kind}: {n}")


if __name__ == "__main__":
    main()