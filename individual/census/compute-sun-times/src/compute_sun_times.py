"""Compute daily sun times for CA Census places and counties.

Output: one row per (geoid, date) with civil dawn, sunrise, sunset, civil
dusk as local (America/Los_Angeles) wall-clock times, plus minutes after
midnight for easy comparison against RIPA TIME_OF_STOP.
"""

import argparse
import datetime as dt
from zoneinfo import ZoneInfo

import polars as pl
from astral import Observer
from astral.sun import dawn, dusk, sunrise, sunset

TZ = ZoneInfo("America/Los_Angeles")
EVENTS = {"dawn": dawn, "sunrise": sunrise, "sunset": sunset, "dusk": dusk}


def load_locations(places_path, counties_path):
    places = pl.read_parquet(places_path).select(
        "geoid", "name", pl.lit("place").alias("geo_type"), "lat", "lon"
    )
    counties = pl.read_parquet(counties_path).select(
        "geoid", "name", pl.lit("county").alias("geo_type"), "lat", "lon"
    )
    return pl.concat([places, counties])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--places", required=True)
    parser.add_argument("--counties", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    dates = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
    locs = load_locations(args.places, args.counties)

    cols = {k: [] for k in ["geoid", "date", *EVENTS]}
    for geoid, lat, lon in locs.select("geoid", "lat", "lon").iter_rows():
        obs = Observer(latitude=lat, longitude=lon)
        for d in dates:
            cols["geoid"].append(geoid)
            cols["date"].append(d)
            for name, fn in EVENTS.items():
                # dawn/dusk default to civil twilight (depression=6)
                cols[name].append(fn(obs, d, tzinfo=TZ).replace(tzinfo=None))

    df = pl.DataFrame(cols).with_columns(
        [pl.col(e).dt.time().alias(e) for e in EVENTS]
        + [
            (pl.col(e).dt.hour().cast(pl.Int16) * 60 + pl.col(e).dt.minute())
            .alias(f"{e}_minute")
            for e in EVENTS
        ]
    )
    df = locs.select("geoid", "name", "geo_type").join(df, on="geoid")

    # Sanity: ordering of events within each day
    assert (df["dawn"] < df["sunrise"]).all()
    assert (df["sunrise"] < df["sunset"]).all()
    assert (df["sunset"] < df["dusk"]).all()

    df.write_parquet(args.output)
    print(f"Wrote {len(df):,} rows ({len(locs)} locations x {len(dates)} days) to {args.output}")


if __name__ == "__main__":
    main()
