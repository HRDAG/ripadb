# ripadb

## Project overview

ripadb is a project to download, store, analyze, and visualize California's
RIPA (Racial and Identity Profiling Act) stop data. RIPA requires law
enforcement agencies to collect and report data on stops, including perceived
demographics, stop reasons, actions taken, and outcomes.

Goals:
- Download and manage RIPA data and annual board reports
- Build a Postgres database to store and index the data
- Provide a simple API to query the data
- Provide a web UI to explore the data (summaries by agency, year, patterns)
- Perform analyses that go deeper than the annual reports
- Eventually: jurisdiction-specific analyses combining RIPA data with census,
  arrests, use-of-force, and other data sources

## Data sources

### RIPA stop data
- Published at: https://openjustice.doj.ca.gov/data (under "RIPA Stop Data")
- Format: ZIP files containing CSV data, one per year
- Example URL: https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2025-05/RIPA-Stop-Data-2023.zip
- PDF README files are also available on the same page
- Data years: 2018 onward (coverage expands as more agencies are phased in)

### RIPA Board annual reports
- Published at: https://oag.ca.gov/ab953/board/reports
- Reports from 2018-2026, including full reports, appendices, executive
  summaries, fact sheets, best practices, and statutorily mandated tables
- The 2026 report (released Jan 30, 2026) covers ~5.1 million stops from 2024

## Project structure

This project uses the **HRDAG task-based workflow**. Work is organized into
pipelines, each containing discrete tasks.

### HRDAG conventions
- Each task has: `Makefile`, `src/`, `input/`, `output/`
- Tasks are self-contained: code in `src/`, outputs in `output/`
- Outputs are reproducible via `make`
- No data files in git -- only code, configs, and symlinks
- Pipelines flow from `import/` through processing tasks to `export/`
- Optional dirs: `hand/` (config), `docs/`, `note/` (notebooks), `frozen/`
- Use relative paths in Makefiles to reference upstream task outputs

### Planned pipelines
- `import/` -- download and stage raw RIPA data and reports
- `clean/` -- clean and normalize the CSV data
- `database/` -- load data into Postgres, define schema and indexes
- `api/` -- API server for querying the database
- `ui/` -- web UI for exploring and visualizing the data
- `analysis/` -- deeper analyses and writeups

## Tech stack

- **Language**: Python (data processing, API), JavaScript/TypeScript (UI)
- **Database**: PostgreSQL
- **Build**: Make (HRDAG-style Makefiles)
- **Data formats**: CSV (raw), Parquet (intermediate), Postgres (final)

## Development conventions

- Keep tasks small and focused
- Write Makefiles so `make` in any task dir reproduces its outputs
- Commit code and config only; keep data out of the repo
- Use `.gitignore` to exclude `output/`, `input/` data files, etc.
