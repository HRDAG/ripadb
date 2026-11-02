"""Attach daily sun times to each RIPA stop, for veil-of-darkness analyses.

One row per stop (DOJ_RECORD_ID): every person in a stop shares the date,
time, and location. Stop location comes from city_crosswalk.parquet; sun
times are for that geography's internal point on the stop date, in local
wall-clock time like TIME_OF_STOP.

`light` classifies the stop time:
  day       sunrise <= t < sunset
  twilight  dawn <= t < sunrise, or sunset <= t < dusk (civil twilight)
  dark      t < dawn, or t >= dusk
"""

import argparse

import polars as pl


def parse_minute(col):
    """Minutes after midnight. 2018-2020 store HMM integers ("930"),
    2021+ store "HH:MM:SS"."""
    c = pl.col(col)
    hhmm = c.str.replace_all(":", "").str.slice(0, 4)
    hhmm = pl.when(c.str.contains(":")).then(hhmm).otherwise(c).cast(pl.Int16)
    return (hhmm // 100) * 60 + hhmm % 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stops", required=True)
    parser.add_argument("--crosswalk", required=True)
    parser.add_argument("--sun-times", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    stops = (
        pl.scan_parquet(args.stops)
        .select(
            pl.col("DOJ_RECORD_ID").alias("doj_record_id"),
            "data_year",
            pl.col("AGENCY_ORI").alias("agency_ori"),
            "county",
            pl.col("LOC_CLOSEST_CITY").alias("loc_closest_city"),
            pl.col("DATE_OF_STOP").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
            parse_minute("TIME_OF_STOP").alias("stop_minute"),
        )
        .unique(subset="doj_record_id", keep="first")
        .collect()
    )
    assert stops["stop_minute"].is_between(0, 1439).all()

    xw = pl.read_parquet(args.crosswalk).select(
        "loc_closest_city", "county", "sun_geoid", "match_method"
    )
    sun = pl.read_parquet(args.sun_times).select(
        pl.col("geoid").alias("sun_geoid"),
        pl.col("geo_type").alias("sun_geo_type"),
        "date", "dawn_minute", "sunrise_minute", "sunset_minute", "dusk_minute",
    )

    n = len(stops)
    df = stops.join(xw, on=["loc_closest_city", "county"], how="left", nulls_equal=True)
    df = df.join(sun, on=["sun_geoid", "date"], how="left")
    assert len(df) == n
    # Every resolved geography must have sun times for the stop date
    assert df.filter(pl.col("sun_geoid").is_not_null())["dusk_minute"].null_count() == 0

    t = pl.col("stop_minute")
    df = df.with_columns(
        pl.when(pl.col("dusk_minute").is_null()).then(None)
        .when((t < pl.col("dawn_minute")) | (t >= pl.col("dusk_minute"))).then(pl.lit("dark"))
        .when((t < pl.col("sunrise_minute")) | (t >= pl.col("sunset_minute"))).then(pl.lit("twilight"))
        .otherwise(pl.lit("day"))
        .alias("light")
    ).sort("doj_record_id")

    df.write_parquet(args.output)
    print(f"{args.output}: {n:,} stops")
    print(df.group_by("light").len().sort("light"))


if __name__ == "__main__":
    main()
