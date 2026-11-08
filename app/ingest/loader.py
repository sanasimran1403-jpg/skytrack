import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()

UPSERT_AIRCRAFT = text("""
       INSERT INTO aircraft (icao24, callsign, country)
       VALUES (:icao24, :callsign, :country)
       ON CONFLICT (icao24) DO UPDATE
       SET callsign = COALESCE(NULLIF(EXCLUDED.callsign, ''), aircraft.callsign),
           country = EXCLUDED.country
   """)

INSERT_POSITION = text("""
       INSERT INTO positions
           (icao24, ts, lat, lon, altitude_m, speed_ms, heading,
            vertical_rate, on_ground, squawk)
       VALUES
           (:icao24, :ts, :lat, :lon, :altitude_m, :speed_ms, :heading,
            :vertical_rate, :on_ground, :squawk)
       ON CONFLICT (icao24, ts) DO NOTHING
   """)


def parse_snapshot(data):
       """OpenSky state vector order:
       0 icao24, 1 callsign, 2 country, 3 time_position, 4 last_contact,
       5 lon, 6 lat, 7 baro_altitude, 8 on_ground, 9 velocity, 10 true_track,
       11 vertical_rate, 12 sensors, 13 geo_altitude, 14 squawk
       """
       snap_time = data.get("time")
       aircraft, positions = {}, []
       for s in data.get("states") or []:
           icao24 = s[0]
           callsign = (s[1] or "").strip()
           t = s[3] or snap_time
           lon, lat = s[5], s[6]
           if lat is None or lon is None or t is None:
               continue
           aircraft[icao24] = {"icao24": icao24, "callsign": callsign, "country": s[2]}
           positions.append({
               "icao24": icao24,
               "ts": datetime.fromtimestamp(t, tz=timezone.utc),
               "lat": lat,
               "lon": lon,
               "altitude_m": s[7] if s[7] is not None else s[13],
               "speed_ms": s[9],
               "heading": s[10],
               "vertical_rate": s[11],
               "on_ground": s[8],
               "squawk": s[14],
           })
       return aircraft, positions


def main():
       ap = argparse.ArgumentParser()
       ap.add_argument("files", nargs="*", help="jsonl files (default: all in data/)")
       args = ap.parse_args()

       files = [Path(f) for f in args.files] or sorted(Path("data").glob("*.jsonl"))
       engine = create_engine(os.environ["DATABASE_URL"])

       all_aircraft, all_positions = {}, []
       for path in files:
           with path.open(encoding="utf-8") as f:
               for line in f:
                   try:
                       data = json.loads(line)
                   except json.JSONDecodeError:
                       continue  # last line may be half-written
                   a, p = parse_snapshot(data)
                   all_aircraft.update(a)
                   all_positions.extend(p)

       with engine.begin() as conn:
           if all_aircraft:
               conn.execute(UPSERT_AIRCRAFT, list(all_aircraft.values()))
           if all_positions:
               conn.execute(INSERT_POSITION, all_positions)

       print(f"files: {len(files)}, aircraft: {len(all_aircraft)}, "
             f"position rows processed: {len(all_positions)}")


if __name__ == "__main__":
       main()
