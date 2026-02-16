# ripadb — Initial Setup & Data Import Plan

## Context

We're bootstrapping the ripadb project from an empty repo. The first concrete
step is to create the data import pipeline that downloads RIPA stop data from
the CA DOJ OpenJustice portal. This lays the foundation for everything
downstream (cleaning, database loading, API, UI, analysis).

## Overall Project Checklist

- [x] Initialize git repo and CLAUDE.md
- [ ] **Set up repo scaffolding** (`.gitignore`, top-level Makefile, directory structure)
- [ ] **Import pipeline: download RIPA stop data** ← current focus
- [ ] Import pipeline: download RIPA board annual reports (PDFs)
- [ ] Clean pipeline: normalize and validate CSV data
- [ ] Database pipeline: Postgres schema, loading, indexes
- [ ] API: simple query server
- [ ] UI: web-based data explorer
- [ ] Analysis: deeper-than-annual-report analyses

## Current Task: Import Pipeline — Download RIPA Stop Data

### Structure (HRDAG workflow)

```
import/
├── Makefile            # orchestrates sub-tasks
└── download-stops/
    ├── Makefile         # drives the download
    ├── src/
    │   └── download.py  # download script
    ├── hand/
    │   └── urls.yaml    # manifest of known download URLs by year
    ├── output/          # downloaded ZIPs and extracted CSVs (gitignored)
    └── input/           # (empty — this is a source task)
```

### Implementation Details

#### 1. Repo scaffolding

Create:
- `.gitignore` — exclude `output/`, `*.csv`, `*.zip`, `*.parquet`, `__pycache__/`, `.venv/`, etc.
- Top-level `Makefile` — list pipelines (just `import` for now)
- `pyproject.toml` — Python project metadata and dependencies (requests, pyyaml); use `uv` for dependency management

#### 2. `import/download-stops/hand/urls.yaml`

A manifest listing each year's data URL and README URL. Since the upload-date
portion of the URL path varies across years, we can't just template them — we
need to record the known URLs explicitly. Example:

```yaml
stops:
  - year: 2019
    zip_url: https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2023-03/RIPA-Stop-Data-2019.zip
  - year: 2020
    zip_url: https://data-openjustice.doj.ca.gov/sites/default/files/dataset/...
  # etc.

readmes:
  - year: 2023
    pdf_url: https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2025-05/RIPA%20Dataset%20Read%20Me%202023.pdf
  # etc.
```

We'll need to visit the DOJ page or probe URLs to fill in the exact URLs for
each year. The script should handle missing/unavailable years gracefully.

#### 3. `import/download-stops/src/download.py`

A Python script that:
- Reads `hand/urls.yaml` for the list of URLs
- Downloads each ZIP to `output/zip/`
- Extracts CSVs to `output/csv/`
- Downloads README PDFs to `output/readme/`
- Is idempotent: skips files that already exist (unless `--force` flag)
- Prints progress to stdout

#### 4. `import/download-stops/Makefile`

```makefile
.PHONY: all clean

all: output/csv

output/csv: src/download.py hand/urls.yaml
	mkdir -p output/zip output/csv output/readme
	python src/download.py --urls hand/urls.yaml --output output

clean:
	rm -rf output/*
```

#### 5. `import/Makefile`

```makefile
.PHONY: all download-stops

all: download-stops

download-stops:
	cd $@ && make
```

### Verification

1. Run `make` in `import/download-stops/` — confirm ZIPs download and CSVs extract
2. Check that `output/csv/` contains CSV files for each year
3. Run `make` again — confirm idempotency (no re-downloads)
4. Spot-check a CSV: confirm it has expected columns (DOJ_RECORD_ID, PERSON_NUMBER, etc.)

### Decisions made

- **URL manifest**: Manual YAML (`hand/urls.yaml`). We'll probe the DOJ site
  to fill in exact URLs during implementation. Can add a scraper later.
- **Python packaging**: `pyproject.toml` + `uv` for fast dependency management.
- **Dependencies**: `requests`, `pyyaml` (minimal to start).
