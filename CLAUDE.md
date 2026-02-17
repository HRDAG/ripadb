# ripadb

## Project overview

ripadb is a project to download, store, analyze, and visualize California's
RIPA (Racial and Identity Profiling Act) stop data, along with supplementary
datasets (census, arrests, use-of-force, court records, CAD logs, etc.).
RIPA requires law enforcement agencies to collect and report data on stops,
including perceived demographics, stop reasons, actions taken, and outcomes.

Goals:
- Download and manage RIPA data (statewide and jurisdiction-specific) and
  supplementary datasets
- Build a Postgres database to store and index linked data
- Provide a simple API to query the data
- Provide a web UI to explore the data (summaries by agency, year, patterns)
- Perform analyses that go deeper than the annual reports, combining multiple
  data sources to study stop outcomes, disparities, and policy impacts

## Data sources

### RIPA statewide stop data
- Published at: https://openjustice.doj.ca.gov/data (under "RIPA Stop Data")
- Format: ZIP files containing XLSX data, one file per county/agency per year
- Data years: 2018 onward (coverage expands as more agencies are phased in;
  8 agencies in 2018, all 58 counties + CHP by 2022)
- Large agencies (LA, CHP) split into quarterly files
- Starting with 2024 data: new fields on consent search requests and refusals

### RIPA Board annual reports
- Published at: https://oag.ca.gov/ab953/board/reports
- Reports from 2018-2026, including full reports, appendices, executive
  summaries, fact sheets, best practices, and statutorily mandated tables
- The 2026 report (released Jan 30, 2026) covers ~5.1 million stops from 2024

### Jurisdiction-specific RIPA data
- Some cities publish RIPA data on open data portals with more detailed fields
  than the statewide data (e.g. fine-grained location, call-for-service links)
- Planned sources: Berkeley, San Francisco, others as identified
- Additional data may come via PRA (Public Records Act) requests

### Supplementary datasets (planned)
- Census data (daytime/nighttime demographics by tract)
- Arrest records
- Use-of-force records
- Court outcome data
- CAD (Computer Aided Dispatch) logs (via PRA requests)
- Calls for service data

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

### Directory structure

```
individual/              # per-dataset import and cleaning
├── RIPA-statewide/      # statewide RIPA data from DOJ OpenJustice
│   ├── download-stops/  # download ZIP/XLSX stop data
│   ├── download-reports/# download board annual reports (PDFs, XLSX)
│   └── clean/           # normalize and validate data
├── RIPA-Berkeley/       # (planned) city-specific RIPA data
├── RIPA-San-Francisco/  # (planned) city-specific RIPA data
├── census/              # (planned) census demographics
├── arrests/             # (planned) arrest records
├── use-of-force/        # (planned) UoF records
├── court/               # (planned) court outcome data
└── CAD/                 # (planned) CAD logs via PRA
match/                   # linking datasets together
database/                # Postgres schema, loading, indexes
api/                     # API server for querying
ui/                      # web UI for exploring and visualizing
analysis/                # deeper analyses and writeups
```

The `individual/` directory uses a `{dataset}/` subdirectory for each data
source. Each dataset directory contains HRDAG-style tasks for import and
cleaning. The `-statewide` modifier distinguishes the DOJ statewide data from
jurisdiction-specific RIPA data that may have more detailed fields.

## Planned analyses

### Stop outcome analysis (linked data)
In jurisdictions where we can obtain fine-grained location data for stops,
along with arrest and court records, link data to analyze outcomes of stops
(arrest rates, use-of-force rates, court outcomes) and how they vary by
geography, demographics, stop reason, and agency.

### Pretextual stop ban impact (difference-in-differences)
Compare trends in discretionary stop rates and racial disparities before and
after pretextual stop bans, using comparable cities without bans as controls.
Key policies: San Francisco Policy 9.07.04(a) (adopted 2023), LAPD Policy
240.06 (March 2022).

### Consent search analysis
Analyze consent search request and refusal rates by race, gender, and age.
Starting with the 2024 RIPA data, new fields capture consent search requests
and whether consent was given or refused.

### Hierarchical modeling of disparities
Comprehensive joint hierarchical modeling of stop and disparity rates across
all jurisdictions, incorporating both statewide and city-level data. Use
overdispersed Poisson models with census daytime/nighttime demographics plus
racial distribution of arrests and/or calls for service as baselines.
Inspiration: https://sites.stat.columbia.edu/gelman/research/unpublished/frisk7.pdf

### CAD comparison (underreporting detection)
Compare RIPA stop reports to CAD (Computer Aided Dispatch) logs to detect
underreporting, following the approach of the LA OIG report that found the
LA Sheriff's Department drastically underreported stops. Expand this analysis
to other jurisdictions using CAD data obtained via PRA.
Reference: https://assets-us-01.kc-usercontent.com/0234f496-d2b7-00b6-17a4-b43e949b70a2/cfe6d276-13c8-4e41-afc4-3e0db72ca166/The%20Sheriff%E2%80%99s%20Department%E2%80%99s%20Underreporting%20of%20Civilian%20Stop%20Data%20to%20the%20California%20Attorney%20General.pdf

### Fraud detection (anomalous reporting patterns)
Identify anomalous patterns in RIPA data that could indicate fraudulent
reporting. An SFPD officer was found systematically miscoding stop
demographics (https://sfstandard.com/2023/09/13/san-francisco-police-officer-misrepresented-race-bias-investigation/),
and in Connecticut officers recorded "ghost" stops of White drivers. Develop
statistical methods to detect such anomalies.

## Tech stack

- **Language**: Python (data processing, API), JavaScript/TypeScript (UI)
- **Database**: PostgreSQL
- **Build**: Make (HRDAG-style Makefiles)
- **Data formats**: XLSX (raw from DOJ), Parquet (intermediate), Postgres (final)

## Development conventions

- Keep tasks small and focused
- Write Makefiles so `make` in any task dir reproduces its outputs
- Commit code and config only; keep data out of the repo
- Use `.gitignore` to exclude `output/`, `input/` data files, etc.
