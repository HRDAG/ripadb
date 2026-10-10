"""Parse a Census Gazetteer tab-delimited file into Parquet.

Keeps GEOID, NAME, LSAD (places only), land area, and the internal point
(INTPTLAT/INTPTLONG), which is what we use as the location's lat/lon.
"""

import argparse

import polars as pl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    df = pl.read_csv(args.input, separator="\t", infer_schema=False)
    # Last header/column carries trailing whitespace in the raw files
    df = df.rename({c: c.strip() for c in df.columns}).with_columns(
        pl.all().str.strip_chars()
    )

    keep = ["GEOID", "NAME", "LSAD", "ALAND_SQMI", "INTPTLAT", "INTPTLONG"]
    df = df.select([c for c in keep if c in df.columns]).with_columns(
        pl.col("ALAND_SQMI").cast(pl.Float64),
        pl.col("INTPTLAT").cast(pl.Float64).alias("lat"),
        pl.col("INTPTLONG").cast(pl.Float64).alias("lon"),
    ).drop("INTPTLAT", "INTPTLONG")
    df = df.rename({c: c.lower() for c in df.columns})

    assert df["geoid"].is_unique().all()
    assert df["lat"].is_between(32, 42.1).all() and df["lon"].is_between(-124.5, -114).all()

    df.write_parquet(args.output)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
