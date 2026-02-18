#!/usr/bin/env python3
"""Read XLSX headers from one file per year to discover actual column names."""

from pathlib import Path
import polars as pl

STOPS_DIR = Path(__file__).parent.parent.parent / "download-stops" / "output" / "data"


def read_headers(xlsx_path: Path) -> list[str]:
    """Read just the header row from an XLSX file."""
    df = pl.read_excel(xlsx_path, read_options={"n_rows": 1})
    return df.columns


def main():
    for year_dir in sorted(STOPS_DIR.iterdir()):
        if not year_dir.is_dir():
            continue
        year = year_dir.name
        xlsx_files = sorted(year_dir.glob("*.xlsx"))
        if not xlsx_files:
            continue

        # Pick a small non-quarterly file if possible
        chosen = xlsx_files[0]
        for f in xlsx_files:
            if "Q1" not in f.name and "Q2" not in f.name and "Q3" not in f.name and "Q4" not in f.name:
                chosen = f
                break

        cols = read_headers(chosen)
        print(f"\n=== {year} ({chosen.name}) — {len(cols)} columns ===")
        print(", ".join(cols))

    # Now compare across years
    print("\n\n=== CROSS-YEAR COMPARISON ===")
    all_cols = {}
    for year_dir in sorted(STOPS_DIR.iterdir()):
        if not year_dir.is_dir():
            continue
        year = year_dir.name
        xlsx_files = sorted(year_dir.glob("*.xlsx"))
        if not xlsx_files:
            continue
        chosen = xlsx_files[0]
        for f in xlsx_files:
            if "Q1" not in f.name and "Q2" not in f.name and "Q3" not in f.name and "Q4" not in f.name:
                chosen = f
                break
        all_cols[year] = read_headers(chosen)

    years = sorted(all_cols.keys())
    # Find columns unique to each year
    all_names = set()
    for cols in all_cols.values():
        all_names.update(cols)

    # Columns present in all years
    common = all_names.copy()
    for cols in all_cols.values():
        common &= set(cols)
    print(f"\nColumns present in ALL years ({len(common)}):")
    print(", ".join(sorted(common)))

    # Columns unique to specific years
    for year in years:
        unique = set(all_cols[year]) - common
        if unique:
            # Check which are truly unique to this year vs shared with some
            truly_unique = set()
            for col in unique:
                other_years = [y for y in years if y != year and col in set(all_cols[y])]
                if not other_years:
                    truly_unique.add(col)
            if truly_unique:
                print(f"\nColumns ONLY in {year} ({len(truly_unique)}):")
                print(", ".join(sorted(truly_unique)))

    # Columns in 2018-2023 but not 2024
    old_only = set(all_cols["2018"]) - set(all_cols["2024"])
    if old_only:
        print(f"\nColumns in 2018 but NOT 2024 ({len(old_only)}):")
        print(", ".join(sorted(old_only)))

    new_only = set(all_cols["2024"]) - set(all_cols["2018"])
    if new_only:
        print(f"\nColumns in 2024 but NOT 2018 ({len(new_only)}):")
        print(", ".join(sorted(new_only)))


if __name__ == "__main__":
    main()
