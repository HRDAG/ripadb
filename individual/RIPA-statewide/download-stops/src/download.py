#!/usr/bin/env python3
"""Download RIPA stop data ZIPs and README PDFs from CA DOJ."""

import argparse
import sys
import zipfile
from pathlib import Path

import requests
import yaml

CHUNK_SIZE = 8192


def download_file(url: str, dest: Path, force: bool = False) -> bool:
    """Download a file from url to dest. Returns True if downloaded."""
    if dest.exists() and not force:
        print(f"  skip (exists): {dest.name}")
        return False

    print(f"  downloading: {url}")
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)

    size_mb = dest.stat().st_size / (1024 * 1024)
    print(f"  saved: {dest.name} ({size_mb:.1f} MB)")
    return True


DATA_EXTENSIONS = {".csv", ".xlsx"}


def extract_zip(zip_path: Path, year_dir: Path) -> None:
    """Extract data files (CSV or XLSX) from a ZIP archive into year_dir."""
    year_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        data_names = [
            n for n in zf.namelist()
            if Path(n).suffix.lower() in DATA_EXTENSIONS
        ]
        if not data_names:
            print(f"  warning: no data files found in {zip_path.name}")
            return
        for name in data_names:
            dest = year_dir / Path(name).name
            if dest.exists():
                print(f"  skip (exists): {dest.name}")
                continue
            zf.extract(name, path=year_dir)
            # If extracted into a subdirectory, move to year_dir root
            extracted = year_dir / name
            if extracted != dest:
                extracted.rename(dest)
                # Clean up empty parent dirs
                for parent in extracted.parents:
                    if parent == year_dir:
                        break
                    try:
                        parent.rmdir()
                    except OSError:
                        break
            print(f"  extracted: {dest.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--urls", required=True, help="Path to urls.yaml manifest")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--force", action="store_true", help="Re-download existing files")
    args = parser.parse_args()

    urls_path = Path(args.urls)
    output_dir = Path(args.output)
    zip_dir = output_dir / "zip"
    data_dir = output_dir / "data"
    readme_dir = output_dir / "readme"

    with open(urls_path) as f:
        manifest = yaml.safe_load(f)

    # Download stop data ZIPs and extract data files
    stops = manifest.get("stops", [])
    print(f"=== Downloading {len(stops)} stop data files ===")
    for entry in stops:
        year = entry["year"]
        url = entry["zip_url"]
        zip_path = zip_dir / f"RIPA-Stop-Data-{year}.zip"

        print(f"\n[{year}]")
        year_dir = data_dir / str(year)
        downloaded = download_file(url, zip_path, force=args.force)
        if downloaded or not any(year_dir.glob("*")):
            extract_zip(zip_path, year_dir)

    # Download README PDFs
    readmes = manifest.get("readmes", [])
    if readmes:
        print(f"\n=== Downloading {len(readmes)} README PDFs ===")
        for entry in readmes:
            year = entry["year"]
            url = entry["pdf_url"]
            pdf_path = readme_dir / f"RIPA-ReadMe-{year}.pdf"
            print(f"\n[{year}]")
            download_file(url, pdf_path, force=args.force)

    print("\nDone.")


if __name__ == "__main__":
    main()
