#!/usr/bin/env python3
"""Join ORI crosswalk with ACS demographics to produce per-agency demographics.

Reads the hand-reviewed crosswalk YAML and ACS Parquet, joins on
(geography_type, fips), and outputs a Parquet file with one row per
(agency_ori, source, rae_code).
"""

import argparse
from pathlib import Path

import polars as pl
import yaml

# ACS column → RIPA rae_code mapping
ACS_TO_RAE = {
    "nh_asian": 1,
    "nh_black": 2,
    "hispanic": 3,
    # 4 = Middle Eastern/South Asian — no Census equivalent
    "nh_aian": 5,
    "nh_nhpi": 6,
    "nh_white": 7,
    "nh_two_or_more": 8,
}


def load_crosswalk(path: Path):
    """Load crosswalk YAML → list of dicts with ori, geography_type, fips."""
    with open(path) as f:
        data = yaml.safe_load(f)

    rows = []
    for ori, entry in data["agencies"].items():
        if entry["geography_type"] == "skip":
            continue
        if entry.get("match_method") == "unmatched":
            continue
        fips = entry.get("fips")
        if not fips:
            continue
        rows.append({
            "agency_ori": ori,
            "geography_type": entry["geography_type"],
            "fips": str(fips),
            "geography_name": entry.get("geography_name", ""),
        })
    return pl.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crosswalk", required=True, help="Path to crosswalk YAML")
    parser.add_argument("--acs", required=True, help="Path to ACS Parquet")
    parser.add_argument("--source", required=True,
                        help="Source label, e.g. 'acs5_2023_residential'")
    parser.add_argument("--output", required=True, help="Output Parquet path")
    args = parser.parse_args()

    print("Loading crosswalk...")
    xwalk = load_crosswalk(Path(args.crosswalk))
    print(f"  {xwalk.height} agencies with geography matches")

    print("Loading ACS data...")
    acs = pl.read_parquet(args.acs)
    print(f"  {acs.height} geography records")

    # Ensure fips columns are strings for joining
    xwalk = xwalk.cast({"fips": pl.Utf8})
    acs = acs.cast({"fips": pl.Utf8})

    # Join crosswalk to ACS on (geography_type, fips)
    joined = xwalk.join(
        acs.select(["geography_type", "fips", "total_pop"] + list(ACS_TO_RAE.keys())),
        on=["geography_type", "fips"],
        how="left",
    )

    matched = joined.filter(pl.col("total_pop").is_not_null())
    unmatched = joined.filter(pl.col("total_pop").is_null())
    if unmatched.height > 0:
        print(f"  WARNING: {unmatched.height} agencies had no ACS match:")
        for row in unmatched.iter_rows(named=True):
            print(f"    {row['agency_ori']} ({row['geography_type']}, {row['fips']})")

    # Pivot to long format: one row per (agency_ori, source, rae_code)
    rows = []
    for rec in matched.iter_rows(named=True):
        ori = rec["agency_ori"]
        total = rec["total_pop"]
        geo_name = rec["geography_name"]

        # rae_code=0: total population
        rows.append({
            "agency_ori": ori,
            "source": args.source,
            "rae_code": 0,
            "population": total,
            "pct": None,
            "geography_name": geo_name,
        })

        # rae_codes 1-8
        for acs_col, rae_code in ACS_TO_RAE.items():
            pop = rec[acs_col]
            pct = round(pop / total * 100, 1) if total > 0 and pop is not None else None
            rows.append({
                "agency_ori": ori,
                "source": args.source,
                "rae_code": rae_code,
                "population": pop if pop is not None else 0,
                "pct": pct,
                "geography_name": geo_name,
            })

        # rae_code=4: MENA — no Census equivalent
        rows.append({
            "agency_ori": ori,
            "source": args.source,
            "rae_code": 4,
            "population": 0,
            "pct": None,
            "geography_name": geo_name,
        })

    result = pl.DataFrame(rows).cast({
        "rae_code": pl.Int16,
        "population": pl.Int64,
        "pct": pl.Float64,
    })

    print(f"Output: {result.height} rows for {matched.height} agencies")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    result.write_parquet(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
