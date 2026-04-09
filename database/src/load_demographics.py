#!/usr/bin/env python3
"""Load jurisdiction demographics Parquet into PostgreSQL.

Reads the agency_demographics.parquet produced by the match/ori-demographics
task and loads it into the jurisdiction_demographics table. This is designed
to run independently of the main stop data load (which is slow).

Requires: the agencies table must already exist (run `make load` first).
"""

import argparse
import io
import os
from pathlib import Path

import polars as pl
import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=ripadb")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True,
                        help="Path to agency_demographics.parquet")
    args = parser.parse_args()

    parquet_path = Path(args.input)
    if not parquet_path.exists():
        raise FileNotFoundError(f"Not found: {parquet_path}")

    print(f"Reading {parquet_path}...")
    df = pl.read_parquet(parquet_path)
    print(f"  {df.height} rows, {df['agency_ori'].n_unique()} agencies")

    with psycopg.connect(DATABASE_URL) as conn:
        # Drop and recreate the table
        conn.execute("DROP TABLE IF EXISTS jurisdiction_demographics CASCADE")
        conn.execute("""
            CREATE TABLE jurisdiction_demographics (
                agency_ori TEXT NOT NULL REFERENCES agencies(agency_ori),
                source TEXT NOT NULL,
                rae_code SMALLINT NOT NULL,
                population BIGINT NOT NULL,
                pct NUMERIC(5,2),
                geography_name TEXT,
                PRIMARY KEY (agency_ori, source, rae_code)
            )
        """)
        conn.execute(
            "CREATE INDEX idx_jd_agency ON jurisdiction_demographics (agency_ori)"
        )
        conn.commit()

        # Load via COPY
        columns = ["agency_ori", "source", "rae_code", "population", "pct",
                    "geography_name"]
        buf = io.BytesIO()
        df.select(columns).write_csv(buf, null_value="\\N")
        buf.seek(0)

        with conn.cursor() as cur:
            with cur.copy(
                "COPY jurisdiction_demographics (agency_ori, source, rae_code, "
                "population, pct, geography_name) "
                "FROM STDIN WITH (FORMAT csv, HEADER true, NULL '\\N')"
            ) as copy:
                while chunk := buf.read(8 * 1024 * 1024):
                    copy.write(chunk)

        conn.commit()

        # Verify
        count = conn.execute(
            "SELECT COUNT(*) FROM jurisdiction_demographics"
        ).fetchone()[0]
        n_agencies = conn.execute(
            "SELECT COUNT(DISTINCT agency_ori) FROM jurisdiction_demographics"
        ).fetchone()[0]
        print(f"  Loaded: {count} rows, {n_agencies} agencies")

    print("Done.")


if __name__ == "__main__":
    main()
