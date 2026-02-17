#!/usr/bin/env python3
"""Download RIPA board annual reports from CA OAG."""

import argparse
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--urls", required=True, help="Path to urls.yaml manifest")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--force", action="store_true", help="Re-download existing files")
    args = parser.parse_args()

    urls_path = Path(args.urls)
    output_dir = Path(args.output)

    with open(urls_path) as f:
        manifest = yaml.safe_load(f)

    reports = manifest.get("reports", [])
    total_files = sum(len(r.get("files", [])) for r in reports)
    print(f"=== Downloading {total_files} files across {len(reports)} years ===")

    for entry in reports:
        year = entry["year"]
        year_dir = output_dir / str(year)
        files = entry.get("files", [])
        print(f"\n[{year}] ({len(files)} files)")

        for f in files:
            dest = year_dir / f["name"]
            download_file(f["url"], dest, force=args.force)

    print("\nDone.")


if __name__ == "__main__":
    main()
