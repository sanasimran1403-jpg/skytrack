import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

URL = "https://opensky-network.org/api/states/all"
# ~81 square degrees (South-Central India) => 2 API credits per call
BBOX = {"lamin": 12.0, "lomin": 74.0, "lamax": 21.0, "lomax": 83.0}


def fetch_once():
    r = requests.get(URL, params=BBOX, timeout=20)
    if r.status_code == 429:
        raise RuntimeError("429 rate limit: daily credits used up, try later")
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=60, help="number of snapshots")
    ap.add_argument("--interval", type=int, default=60, help="seconds between calls")
    args = ap.parse_args()

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"opensky_{datetime.now(timezone.utc):%Y%m%d_%H%M}.jsonl"

    with out.open("a", encoding="utf-8") as f:
        for i in range(args.count):
            try:
                data = fetch_once()
            except Exception as e:
                print(f"[{i + 1}/{args.count}] error: {e}")
                if "429" in str(e):
                    break
                time.sleep(args.interval)
                continue

            n = len(data.get("states") or [])
            f.write(json.dumps(data) + "\n")
            f.flush()
            print(f"[{i + 1}/{args.count}] saved {n} aircraft -> {out}")
            if i < args.count - 1:
                time.sleep(args.interval)


if __name__ == "__main__":
    main()