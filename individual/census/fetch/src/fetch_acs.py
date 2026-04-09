#!/usr/bin/env python3
"""Fetch ACS 5-Year table B03002 (Hispanic/Latino Origin by Race)
for all California places, counties, and the state total.

Outputs a single Parquet file with columns:
  geography_type, fips, name, total_pop, and per-race population columns
  mapped to RIPA rae_codes.
"""

import argparse
from pathlib import Path

import polars as pl
from census import Census
from dotenv import load_dotenv
import os

# B03002 variables we need
ACS_VARS = {
    "B03002_001E": "total_pop",
    "B03002_003E": "nh_white",       # rae_code 7
    "B03002_004E": "nh_black",       # rae_code 2
    "B03002_005E": "nh_aian",        # rae_code 5
    "B03002_006E": "nh_asian",       # rae_code 1
    "B03002_007E": "nh_nhpi",        # rae_code 6
    "B03002_009E": "nh_two_or_more", # rae_code 8
    "B03002_012E": "hispanic",       # rae_code 3
}

CA_FIPS = "06"


def fetch_geography(c: Census, vintage: int, geo_type: str):
    """Fetch B03002 for a California geography type."""
    fields = ("NAME",) + tuple(ACS_VARS.keys())

    if geo_type == "place":
        raw = c.acs5.state_place(fields, CA_FIPS, Census.ALL, year=vintage)
        fips_key = "place"
    elif geo_type == "county":
        raw = c.acs5.state_county(fields, CA_FIPS, Census.ALL, year=vintage)
        fips_key = "county"
    elif geo_type == "state":
        raw = c.acs5.get(fields, {"for": "state:06"}, year=vintage)
        fips_key = "state"
    else:
        raise ValueError(f"Unknown geography type: {geo_type}")

    rows = []
    for rec in raw:
        row = {
            "geography_type": geo_type,
            "fips": str(rec[fips_key]),
            "name": rec["NAME"],
        }
        for acs_var, col_name in ACS_VARS.items():
            val = rec.get(acs_var)
            row[col_name] = int(val) if val is not None else None
        rows.append(row)

    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vintage", type=int, default=2023,
                        help="ACS 5-year vintage (default: 2023)")
    parser.add_argument("--output", required=True, help="Output Parquet path")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("CENSUS_API_KEY")
    if not api_key:
        raise RuntimeError("CENSUS_API_KEY not found in environment or .env")

    c = Census(api_key)

    all_rows = []
    for geo in ("place", "county", "state"):
        print(f"Fetching {geo}...")
        rows = fetch_geography(c, args.vintage, geo)
        print(f"  {len(rows)} records")
        all_rows.extend(rows)

    df = pl.DataFrame(all_rows)

    # Ensure integer types for population columns
    pop_cols = list(ACS_VARS.values())
    df = df.cast({c: pl.Int64 for c in pop_cols})

    print(f"Total records: {df.height}")
    print(f"  Places: {df.filter(pl.col('geography_type') == 'place').height}")
    print(f"  Counties: {df.filter(pl.col('geography_type') == 'county').height}")
    print(f"  State: {df.filter(pl.col('geography_type') == 'state').height}")

    # Sanity check: California total population
    state_row = df.filter(pl.col("geography_type") == "state")
    if state_row.height == 1:
        total = state_row["total_pop"][0]
        print(f"  CA total population: {total:,}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
