#!/usr/bin/env python3
"""Load cleaned RIPA Parquet files into PostgreSQL.

Reads each year's Parquet file, streams rows into the stops table via
psycopg COPY, then builds indexes and materialized views.
"""

import argparse
import io
import os
import sys
from pathlib import Path

import polars as pl
import psycopg
from psycopg import sql


DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=ripadb")
DB_NAME = "ripadb"
# Connect to default 'postgres' db for admin operations
ADMIN_URL = "dbname=postgres"

YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]


def ensure_database():
    """Create the database if it doesn't exist."""
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,)
        ).fetchone()
        if not exists:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Created database: {DB_NAME}")
        else:
            print(f"Database exists: {DB_NAME}")


def ensure_extensions(conn):
    """Create required extensions."""
    conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    conn.commit()


def apply_schema(conn, schema_path: Path):
    """Run the schema SQL to create tables, indexes, and views."""
    # Only run the DDL up to the agencies INSERT (stops must be loaded first)
    schema_sql = schema_path.read_text()

    # Split into: pre-data DDL (create tables, lookups) and post-data DDL
    # (agencies insert, materialized views)
    # We'll find where the agencies INSERT starts
    marker = "INSERT INTO agencies"
    idx = schema_sql.index(marker)

    # Find the CREATE TABLE agencies line before it
    agencies_create_idx = schema_sql.rindex("CREATE TABLE agencies", 0, idx)

    pre_data_sql = schema_sql[:agencies_create_idx]
    post_data_sql = schema_sql[agencies_create_idx:]

    return pre_data_sql, post_data_sql


def get_stops_columns(conn):
    """Get ordered column names from the stops table (excluding id)."""
    cur = conn.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'stops' AND column_name != 'id'
        ORDER BY ordinal_position
    """)
    return [row[0] for row in cur.fetchall()]


def load_year(conn, parquet_path: Path, columns: list[str]):
    """Load a single Parquet file into the stops table."""
    print(f"  Reading {parquet_path.name}...")
    df = pl.read_parquet(parquet_path)

    # Lowercase column names to match Postgres
    df = df.rename({c: c.lower() for c in df.columns})

    # Ensure column order matches the table
    df = df.select(columns)

    print(f"  Writing {df.height:,} rows...")

    # Stream CSV to Postgres via COPY
    buf = io.BytesIO()
    df.write_csv(buf, null_value="\\N")
    buf.seek(0)

    with conn.cursor() as cur:
        with cur.copy(
            sql.SQL("COPY stops ({}) FROM STDIN WITH (FORMAT csv, HEADER true, NULL '\\N')").format(
                sql.SQL(", ").join(sql.Identifier(c) for c in columns)
            )
        ) as copy:
            while chunk := buf.read(8 * 1024 * 1024):  # 8MB chunks
                copy.write(chunk)

    conn.commit()
    print(f"  Loaded {parquet_path.name}: {df.height:,} rows")
    return df.height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", required=True,
        help="Directory containing year.parquet files"
    )
    parser.add_argument(
        "--schema", required=True,
        help="Path to schema.sql"
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    schema_path = Path(args.schema)

    # Step 1: Ensure database exists
    print("=== Step 1: Ensure database ===")
    ensure_database()

    # Step 2: Apply pre-data schema (drop/create tables, lookups)
    print("=== Step 2: Apply schema (tables, lookups) ===")
    pre_data_sql, post_data_sql = apply_schema(None, schema_path)

    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        ensure_extensions(conn)

    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(pre_data_sql)
        conn.commit()
        print("  Created tables and lookups")

        # Step 3: Load data year by year
        print("=== Step 3: Load stop data ===")
        columns = get_stops_columns(conn)
        total = 0
        for year in YEARS:
            parquet_path = input_dir / f"{year}.parquet"
            if not parquet_path.exists():
                print(f"  Skipping {year}: {parquet_path} not found")
                continue
            total += load_year(conn, parquet_path, columns)

        print(f"  Total rows loaded: {total:,}")

        # Step 4: Apply post-data schema (agencies table, materialized views)
        print("=== Step 4: Build agencies table and materialized views ===")
        conn.execute(post_data_sql)
        conn.commit()
        print("  Created agencies table and materialized views")

    # Step 5: Verify
    print("=== Step 5: Verify ===")
    with psycopg.connect(DATABASE_URL) as conn:
        stops_count = conn.execute("SELECT COUNT(*) FROM stops").fetchone()[0]
        agencies_count = conn.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
        race_mv_count = conn.execute("SELECT COUNT(*) FROM mv_agency_year_race").fetchone()[0]
        gender_mv_count = conn.execute("SELECT COUNT(*) FROM mv_agency_year_gender").fetchone()[0]
        age_mv_count = conn.execute("SELECT COUNT(*) FROM mv_agency_year_age").fetchone()[0]

        print(f"  stops: {stops_count:,} rows")
        print(f"  agencies: {agencies_count:,} rows")
        print(f"  mv_agency_year_race: {race_mv_count:,} rows")
        print(f"  mv_agency_year_gender: {gender_mv_count:,} rows")
        print(f"  mv_agency_year_age: {age_mv_count:,} rows")

    print("=== Done ===")


if __name__ == "__main__":
    main()
