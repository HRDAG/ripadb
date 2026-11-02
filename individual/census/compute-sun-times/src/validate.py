"""Spot-check computed sun times against the US Naval Observatory API.

USNO Astronomical Applications Dept. publishes rise/set/twilight times
(https://aa.usno.navy.mil/data/api), rounded to the minute. Fails if any
sampled time differs from USNO by more than TOLERANCE minutes.
"""

import argparse
import time

import polars as pl
import requests

URL = "https://aa.usno.navy.mil/api/rstt/oneday"
USNO_PHEN = {
    "Begin Civil Twilight": "dawn",
    "Rise": "sunrise",
    "Set": "sunset",
    "End Civil Twilight": "dusk",
}
TOLERANCE = 1  # minutes; USNO rounds to the minute


def usno_times(date, lat, lon, retries=5):
    params = {"date": str(date), "coords": f"{lat},{lon}", "tz": -8, "dst": "true"}
    for attempt in range(retries):
        r = requests.get(URL, params=params, timeout=30)
        if r.status_code < 500:
            break
        time.sleep(2**attempt)  # USNO API intermittently returns 502
    r.raise_for_status()
    out = {}
    for item in r.json()["properties"]["data"]["sundata"]:
        if item["phen"] in USNO_PHEN:
            hh, mm = item["time"].split()[0].split(":")
            out[USNO_PHEN[item["phen"]]] = int(hh) * 60 + int(mm)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--gazetteer", required=True)
    parser.add_argument("--n", type=int, default=40)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    gaz = pl.concat([
        pl.read_parquet(f"{args.gazetteer}/ca_{t}.parquet").select("geoid", "lat", "lon")
        for t in ("places", "counties")
    ])
    sample = (
        pl.read_parquet(args.input)
        .sample(args.n, seed=args.seed)
        .join(gaz, on="geoid")
    )

    rows = []
    for r in sample.iter_rows(named=True):
        usno = usno_times(r["date"], r["lat"], r["lon"])
        for event, usno_min in usno.items():
            ours = r[event].hour * 60 + r[event].minute + r[event].second / 60
            rows.append({
                "geoid": r["geoid"], "name": r["name"], "date": r["date"],
                "event": event, "ours": str(r[event]), "usno_minute": usno_min,
                "diff_minutes": round(ours - usno_min, 2),
            })
        time.sleep(0.5)

    df = pl.DataFrame(rows)
    df.write_csv(args.output)
    worst = df["diff_minutes"].abs().max()
    print(f"{len(df)} comparisons; max |diff| = {worst} min")
    assert worst <= TOLERANCE, f"sun times disagree with USNO by up to {worst} min"


if __name__ == "__main__":
    main()
