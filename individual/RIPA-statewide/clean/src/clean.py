#!/usr/bin/env python3
"""Clean and normalize RIPA statewide stop data XLSX files into Parquet.

Reads XLSX files from download-stops output, applies canonical column renames,
coerces types, adds metadata columns, and writes one Parquet file per year
with a common schema (the union of all columns across all years).
"""

import argparse
import re
import sys
from pathlib import Path

import polars as pl
import yaml

# Columns that should always be read as strings (CJIS codes, school codes, etc.)
STRING_COLUMNS = {
    "DOJ_RECORD_ID",
    "AGENCY_ORI",
    "AGENCY_NAME",
    "SCHOOL_CODE",
    "SCHOOL_NAME",
    "LOC_CLOSEST_CITY",
    "CLOSEST_CITY",
    "RFS_TRAFFIC_VIOLATION_CODE",
    "RFS_RS_CODE",
    "RFS_PC_CODE",
    "ROS_WARNING_CDS",
    "ROS_CITATION_CDS",
    "ROS_IN_FIELD_CITE_RELEASE_CDS",
    "ROS_CUSTODIAL_WOUT_WARRANT_CDS",
    "ROS_VERBAL_WARNING_CDS",
    "ROS_WRITTEN_WARNING_CDS",
}

# AGE_GROUP bin edges: [0,10) -> 1, [10,15) -> 2, [15,18) -> 3, etc.
AGE_GROUP_EDGES = [0, 10, 15, 18, 25, 35, 45, 55, 65]
AGE_GROUP_LABELS = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def load_schema(schema_path: Path) -> dict:
    """Load the schema YAML config."""
    with open(schema_path) as f:
        return yaml.safe_load(f)


def parse_filename(filename: str) -> tuple[str, int | None]:
    """Extract county and quarter from an XLSX filename.

    Examples:
        "RIPA Stop Data _ Riverside 2018.xlsx"       -> ("Riverside", None)
        "RIPA Stop Data _ Los Angeles 2018 Q3.xlsx"  -> ("Los Angeles", 3)
        "RIPA Stop Data_Alameda 2024_final.xlsx"     -> ("Alameda", None)
        "RIPA Stop Data_Los Angeles 2024 Q1_final.xlsx" -> ("Los Angeles", 1)
        "12312022 Supplement RIPA SD final.xlsx"      -> ("Supplement", None)
    """
    stem = filename.replace(".xlsx", "")

    # Handle the 2022 supplement file
    if "Supplement" in stem:
        return "Supplement", None

    # Strip trailing _final / _Final / final
    stem = re.sub(r"[_ ]?[Ff]inal$", "", stem)

    # Remove the "RIPA Stop Data" prefix (with varying separators)
    stem = re.sub(r"^RIPA Stop Data[_ ]+", "", stem)

    # Now we have something like "Los Angeles 2024 Q1" or "Alameda 2024"
    # or "CHP 2024 Q1" or "Riverside 2018"
    quarter = None
    qmatch = re.search(r"\s+Q(\d)$", stem)
    if qmatch:
        quarter = int(qmatch.group(1))
        stem = stem[: qmatch.start()]

    # Remove the year at the end
    stem = re.sub(r"\s+\d{4}$", "", stem)

    county = stem.strip()
    return county, quarter


def read_xlsx(path: Path) -> pl.DataFrame:
    """Read an XLSX file, forcing string columns where needed."""
    # Build schema overrides for columns we know should be strings
    # We read with calamine engine (default for polars) which is fast
    df = pl.read_excel(path, infer_schema_length=0)  # read all as string first
    return df


def coerce_types(df: pl.DataFrame) -> pl.DataFrame:
    """Cast columns to appropriate types."""
    casts = {}
    for col in df.columns:
        if col in STRING_COLUMNS or col in (
            "data_year", "county", "quarter", "source_file",
            "TIME_OF_STOP",
        ):
            continue  # keep as string

        series = df[col]
        if series.dtype == pl.String:
            # Try to determine the right type
            if col in ("DATE_OF_STOP",):
                # Will handle date parsing separately
                continue
            elif col in ("PERSON_NUMBER", "STOP_DURATION", "AGE",
                         "REASON_FOR_STOP", "AGE_GROUP", "age_group_orig",
                         "RFS_TRAFFIC_VIOLATION_TYPE", "RFS_EC_DISCIPLINE_CODE",
                         "RFS_EC_DISCIPLINE"):
                casts[col] = pl.Int32
            else:
                # Most flag columns are 0/1 or small integers
                casts[col] = pl.Int8

    # Apply casts, tolerating nulls from non-numeric strings
    for col, dtype in casts.items():
        if col in df.columns:
            df = df.with_columns(
                pl.col(col).cast(dtype, strict=False).alias(col)
            )

    return df


def apply_renames(df: pl.DataFrame, renames: dict[str, str]) -> pl.DataFrame:
    """Rename columns according to the canonical rename map."""
    # Only rename columns that actually exist in this DataFrame
    active_renames = {k: v for k, v in renames.items() if k in df.columns}
    if active_renames:
        df = df.rename(active_renames)
    return df


def remap_pd_disab_multi(df: pl.DataFrame) -> pl.DataFrame:
    """Remap PD_MULTI values for years that had PD_DISAB_MULTI.

    PD_DISAB_MULTI used: 1 (one disability), 2 (multiple), Blank (none)
    PD_MULTI uses: 0 (none), 1 (one), 2 (multiple)

    After rename, PD_DISAB_MULTI is already called PD_MULTI.
    We need to map Blank/null -> 0. The 1 and 2 values are the same.
    """
    if "PD_MULTI" in df.columns:
        df = df.with_columns(
            pl.col("PD_MULTI").fill_null(0).alias("PD_MULTI")
        )
    return df


def derive_sor_straight(df: pl.DataFrame) -> pl.DataFrame:
    """Derive SOR_STRAIGHT from SOR_LGB for pre-2024 data."""
    if "SOR_LGB" in df.columns and "SOR_STRAIGHT" not in df.columns:
        df = df.with_columns(
            pl.when(pl.col("SOR_LGB").is_not_null())
            .then(1 - pl.col("SOR_LGB"))
            .otherwise(None)
            .cast(pl.Int8)
            .alias("SOR_STRAIGHT")
        )
    return df


def derive_age_group(df: pl.DataFrame) -> pl.DataFrame:
    """Derive a consistent AGE_GROUP from AGE, preserving original as age_group_orig."""
    if "AGE_GROUP" in df.columns:
        df = df.rename({"AGE_GROUP": "age_group_orig"})

    if "AGE" in df.columns:
        # Build a when/then chain for age bins
        expr = pl.lit(None).cast(pl.Int8)
        for i in range(len(AGE_GROUP_EDGES)):
            lo = AGE_GROUP_EDGES[i]
            label = AGE_GROUP_LABELS[i]
            if i < len(AGE_GROUP_EDGES) - 1:
                hi = AGE_GROUP_EDGES[i + 1]
                expr = (
                    pl.when((pl.col("AGE") >= lo) & (pl.col("AGE") < hi))
                    .then(pl.lit(label, dtype=pl.Int8))
                    .otherwise(expr)
                )
            else:
                # Last bin: 65+
                expr = (
                    pl.when(pl.col("AGE") >= lo)
                    .then(pl.lit(label, dtype=pl.Int8))
                    .otherwise(expr)
                )
        df = df.with_columns(expr.alias("AGE_GROUP"))
    else:
        df = df.with_columns(pl.lit(None).cast(pl.Int8).alias("AGE_GROUP"))

    if "age_group_orig" not in df.columns:
        df = df.with_columns(pl.lit(None).cast(pl.Int8).alias("age_group_orig"))

    return df


def add_metadata(
    df: pl.DataFrame,
    data_year: int,
    county: str,
    quarter: int | None,
    source_file: str,
) -> pl.DataFrame:
    """Add metadata columns."""
    return df.with_columns(
        pl.lit(data_year).cast(pl.Int16).alias("data_year"),
        pl.lit(county).alias("county"),
        pl.lit(quarter).cast(pl.Int8).alias("quarter"),
        pl.lit(source_file).alias("source_file"),
    )


def align_to_schema(df: pl.DataFrame, target_columns: list[str]) -> pl.DataFrame:
    """Add missing columns as null and reorder to match target schema."""
    for col in target_columns:
        if col not in df.columns:
            df = df.with_columns(pl.lit(None).cast(pl.Null).alias(col))

    # Drop any columns not in target schema
    extra = set(df.columns) - set(target_columns)
    if extra:
        print(f"    warning: dropping {len(extra)} unexpected columns: {sorted(extra)}")
        df = df.drop(list(extra))

    return df.select(target_columns)


def process_file(
    xlsx_path: Path,
    data_year: int,
    renames: dict[str, str],
    has_pd_disab_multi: bool,
) -> pl.DataFrame:
    """Process a single XLSX file."""
    county, quarter = parse_filename(xlsx_path.name)
    print(f"  {xlsx_path.name} -> county={county}, quarter={quarter}")

    df = read_xlsx(xlsx_path)
    df = apply_renames(df, renames)
    df = coerce_types(df)

    if has_pd_disab_multi:
        df = remap_pd_disab_multi(df)

    df = derive_sor_straight(df)
    df = derive_age_group(df)
    df = add_metadata(df, data_year, county, quarter, xlsx_path.name)

    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True, help="Data year to process")
    parser.add_argument("--input", required=True, help="Input directory with XLSX files")
    parser.add_argument("--schema", required=True, help="Path to schema.yaml")
    parser.add_argument("--output", required=True, help="Output Parquet path")
    args = parser.parse_args()

    schema = load_schema(Path(args.schema))
    renames = schema.get("renames", {})
    target_columns = schema["columns"]
    input_dir = Path(args.input)
    output_path = Path(args.output)

    xlsx_files = sorted(input_dir.glob("*.xlsx"))
    if not xlsx_files:
        print(f"No XLSX files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    has_pd_disab_multi = args.year <= 2020  # 2018-2020 have PD_DISAB_MULTI

    print(f"=== Processing {args.year}: {len(xlsx_files)} files ===")

    frames = []
    for xlsx_path in xlsx_files:
        df = process_file(xlsx_path, args.year, renames, has_pd_disab_multi)
        frames.append(df)

    print(f"  Concatenating {len(frames)} DataFrames...")
    combined = pl.concat(frames, how="diagonal_relaxed")

    print(f"  Aligning to target schema ({len(target_columns)} columns)...")
    combined = align_to_schema(combined, target_columns)

    # Type coercion after alignment
    combined = coerce_types(combined)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.write_parquet(output_path)

    print(f"  Written: {output_path} ({combined.height:,} rows, {output_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # Summary stats
    null_pct = {
        col: combined[col].null_count() / combined.height * 100
        for col in ["DOJ_RECORD_ID", "AGENCY_ORI", "DATE_OF_STOP", "RAE_FULL",
                     "G_FULL", "AGE", "REASON_FOR_STOP"]
        if col in combined.columns
    }
    for col, pct in null_pct.items():
        if pct > 0:
            print(f"    {col}: {pct:.2f}% null")


if __name__ == "__main__":
    main()
