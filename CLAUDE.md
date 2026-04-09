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
├── census/
│   └── fetch/           # ACS 5-Year B03002 demographics via Census API
├── arrests/             # (planned) arrest records
├── use-of-force/        # (planned) UoF records
├── court/               # (planned) court outcome data
└── CAD/                 # (planned) CAD logs via PRA
database/                # Load cleaned Parquet → Postgres, materialized views
├── Makefile             # `make load`, `make refresh`, `make load-demographics`
├── src/
│   ├── schema.sql       # DDL: tables, indexes, materialized views
│   ├── load.py          # Parquet → Postgres via polars + psycopg COPY
│   └── load_demographics.py  # Load jurisdiction demographics independently
└── hand/
    └── lookups.yaml     # Code→label maps (RAE_FULL, G_FULL, etc.)
api/                     # FastAPI app (API + htmx UI) — agency explorer
├── Makefile             # `make run` starts uvicorn dev server on :8000
├── src/
│   ├── app.py           # FastAPI routes + startup
│   ├── db.py            # psycopg connection pool
│   ├── queries.py       # SQL queries for agency explorer
│   └── templates/       # Jinja2 templates
│       ├── base.html    # Layout (htmx + Chart.js includes)
│       ├── index.html   # Agency search/list page
│       ├── agency.html  # Agency detail page (overview tab + chart)
│       └── partials/    # htmx fragments
│           ├── agency_list.html  # Search results table
│           └── agency_tabs.html  # Demographics + disparities tabs
└── static/
    ├── style.css
    ├── htmx.min.js      # Vendored htmx 2.0.4
    └── chart.umd.min.js # Vendored Chart.js 4.4.7
match/                   # linking datasets together
└── ori-demographics/    # ORI → Census geography crosswalk + join
    ├── hand/crosswalk.yaml  # Reviewed ORI→FIPS mapping
    └── src/
        ├── build_crosswalk.py   # Generate crosswalk from agencies table
        └── join_demographics.py # Join crosswalk × ACS → demographics
analysis/                # (planned) deeper analyses and writeups
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

## RIPA statewide data schema

The schema evolved significantly across years. Each row is a person-stop
(one DOJ_RECORD_ID can have multiple PERSON_NUMBERs if multiple people were
involved in a single stop). Key structural differences by era:

### Schema eras

**2018-2023 (columns A-EL, ~142 columns)**
- 2018: only 6 months (Jul-Dec), 8 agencies (wave 1: 1000+ officers)
- 2019: wave 2 added (667+ officers)
- 2020: same agencies as 2019
- 2021: wave 3 added (334+ officers)
- 2022-2023: all agencies reporting (wave 4: 1+ officers joined by 2022)
- Gender: G_MALE, G_FEMALE, G_TRANSGENDER_MAN, G_TRANSGENDER_WOMAN,
  G_GENDER_NONCONFORMING, G_MULTIGENDER; G_FULL values: 1-5
- Sexual orientation: single LGBT field (0/1)
- Actions taken: ADS_* prefix (combined force and non-force actions)
- REASON_FOR_STOP: values 1-8 only
- Result of stop: ROS_WARNING (combined verbal+written)
- No type-of-stop fields (TOS_VEHICULAR, etc.)
- No PERSON_UNHOUSED, PASSENGER_IN_VEHICLE, INSIDE_RESIDENCE,
  WELFARE_WELLNESS_CHECK, NON_REPORTING_AGENCY
- No "Reason Given" (RFS_RG_*) or "Probable Cause" (RFS_PC_*) columns
- Disability multi: PD_DISAB_MULTI in 2018-2020 (values: 1/2/Blank),
  PD_MULTI in 2021-2023 (values: 0/1/2)
- AGE_GROUP bins: 2018-2022 use (1)1-9...(9)65+; 2023 uses different bins
  with 10 groups: (1)1-7, (2)8-11, (3)12-14, (4)15-17, (5)18-24...(10)65+

**2024 (columns A-GT, ~202 columns) — major schema overhaul**
- Actions split: NFA_* (non-force) + OFA_* (force), many new subcategories
- Added: NON_REPORTING_AGENCY, PERSON_UNHOUSED, PASSENGER_IN_VEHICLE,
  INSIDE_RESIDENCE, WELFARE_WELLNESS_CHECK
- Added: TOS_VEHICULAR, TOS_BICYCLE, TOS_PEDESTRIAN, CALL_FOR_SERVICE
- Added: RFS_PC_* (Probable Cause) and RFS_RG_* (Reason Given) column groups
- Gender renamed: G_CISGENDER_MAN, G_CISGENDER_WOMAN, G_NONBINARY_PERSON
- Sexual orientation split: SOR_LGB, SOR_STRAIGHT (replacing single LGBT)
- Race renamed: RAE_HISPANIC_LATINEX (was RAE_HISPANIC_LATINO)
- Location renamed: LOC_CLOSEST_CITY (was CLOSEST_CITY)
- Result split: ROS_WRITTEN_WARNING, ROS_VERBAL_WARNING (separate)
- REASON_FOR_STOP expanded: values 1-10 (added 9=probable cause to arrest,
  10=W&I Code 5150)
- Disability multi: PD_MULTI (values: 0/1/2)
- New consent fields: NFA_SEARCH_PERS_CONSENT, NFA_SEARCH_PROP_CONSENT,
  CTP_VERBAL, CTP_WRITTEN, CTP_IMPLIED
- AGE_GROUP field added

### Common fields across all years
- DOJ_RECORD_ID, PERSON_NUMBER (composite key for a person-stop)
- AGENCY_ORI, AGENCY_NAME
- TIME_OF_STOP, DATE_OF_STOP, STOP_DURATION
- LOC_CLOSEST_CITY (called CLOSEST_CITY in 2018-2023)
- SCHOOL_CODE, SCHOOL_NAME, STOP_STUDENT, K12_SCHOOL_GROUNDS
- RAE_FULL + individual race flags (RAE_ASIAN through RAE_WHITE, RAE_MULTIRACIAL)
- G_FULL + individual gender flags
- AGE, LIMITED_ENGLISH_FLUENCY
- PD_FULL + individual disability flags
- REASON_FOR_STOP + reason subcategory fields
- Basis for search (BFS_*), contraband/evidence (CED_*), property seizure
  basis (BPS_*), type of property seized (TPS_*)
- Result of stop (ROS_*) fields

### File naming patterns
- 2018-2019: `RIPA Stop Data _ {County} {Year}.xlsx` (note space-underscore-space)
- 2020-2021: same pattern
- 2022: `RIPA Stop Data _ {County} {Year} final.xlsx`
- 2023: `RIPA Stop Data_{County} {Year}_Final.xlsx` (underscore, no spaces around it)
- 2024: `RIPA Stop Data_{County} {Year}_final.xlsx` (lowercase "final")
- Quarterly files: `...{County} {Year} Q{1-4}...`

### Data notes
- CJIS codes in RIPA do NOT have leading zeros (e.g. "3" not "00003")
- Data is per-county: file contains all agencies with ORI in that county
- CHP data is separate from county files due to statewide jurisdiction
- ~1% of records have known errors that passed validation (per README)
- 2018 had 28,148 cases of "consensual encounter resulting in search" with
  no search indicated (likely a misunderstanding of the form by officers)

## Implementation status

### Completed
- `individual/RIPA-statewide/download-stops/`: downloads 7 years (2018-2024)
  of RIPA stop data ZIPs, extracts XLSX files to `output/data/{year}/`
- `individual/RIPA-statewide/download-reports/`: downloads 55 board report
  files (2018-2026) to `output/{year}/`
- `individual/RIPA-statewide/clean/`: normalizes XLSX files into Parquet with
  a common 235-column union schema across all years. Outputs one Parquet file
  per year to `output/{year}.parquet`. Handles canonical column renames
  (e.g. G_MALE→G_CISGENDER_MAN, LGBT→SOR_LGB), derives SOR_STRAIGHT from
  SOR_LGB for 2018-2023, derives consistent AGE_GROUP from AGE, and remaps
  PD_DISAB_MULTI→PD_MULTI for 2018-2020. Schema config in `hand/schema.yaml`.
  Total: ~26.3M person-stop rows across 7 years.
- `database/`: Loads all 7 Parquet files into Postgres (`ripadb` database).
  `stops` table with all 235 columns (lowercased), `agencies` dimension table
  (555 agencies), lookup tables for code→label mappings, and 4 materialized
  views for pre-aggregated disparity analysis:
  - `mv_agency_year_race` (12,273 rows) — all stops by agency × year × race
  - `mv_agency_year_race_equip` (10,313 rows) — equipment violations only
  - `mv_agency_year_gender` (6,892 rows) — by agency × year × gender
  - `mv_agency_year_age` (13,735 rows) — by agency × year × age group
  Materialized views harmonize era-split columns (ADS_* vs NFA_*/OFA_*,
  ROS_WARNING vs ROS_WRITTEN/VERBAL_WARNING, etc.). Run `make -C database`
  to load, `make -C database refresh` to refresh views.
- `api/`: FastAPI + htmx agency explorer web app. Serves HTML with htmx for
  interactivity and Chart.js for charts. Features:
  - Agency search with live filtering (debounced htmx)
  - Agency detail page: stops-per-year bar chart, year-over-year table
  - Demographics tab: race, gender, age breakdowns with year filter
  - Disparities tab: search/force/arrest/hit rates by race with disparity
    ratios vs White as reference group, color-coded (1.5x, 2x thresholds)
  - Stop-type filter on disparities: "All stops" or "Equipment violations"
    (high-discretion pretextual stop indicator)
  Run `make -C api run` to start on http://localhost:8000
- `individual/census/fetch/`: downloads ACS 5-Year B03002 (race/ethnicity)
  for all CA places, counties, and state via Census API. Uses python-dotenv
  for `CENSUS_API_KEY` from `.env`. Run `make -C individual/census/fetch`.
- `match/ori-demographics/`: builds ORI→Census geography crosswalk
  (city PD→place FIPS, sheriff→county FIPS, CHP→state, special→skip),
  joins with ACS data to produce per-agency demographics Parquet.
  Crosswalk in `hand/crosswalk.yaml` (395 agencies matched, ~160 skipped).
  Run `make -C match/ori-demographics`.
- `database/`: `jurisdiction_demographics` table loaded independently via
  `make -C database load-demographics`. Keyed by (agency_ori, source,
  rae_code). rae_code 0=total, 1-8=race codes, 4 (MENA)=no Census equiv.
  Includes `geography_name` for display.
- `api/`: Demographics and disparities tabs show Pop %, Stop/Pop ratio
  (stop share / pop share). Agency header shows jurisdiction name and
  population. Graceful degradation when demographics not loaded.
- All scripts are idempotent; dependencies managed via `pyproject.toml` + `uv`

### Database connection
Postgres via Unix socket (peer auth). Database: `ripadb`. Override with
`DATABASE_URL` env var (e.g. `DATABASE_URL=postgresql://user:pass@host/ripadb`
for remote deployment). Default: `dbname=ripadb` (libpq conninfo format).

### Next steps
- Deploy to droplet (pg_dump/restore, systemd + nginx)
- Additional stop-type filters (moving violations, reasonable suspicion, etc.)
- Jurisdiction-specific RIPA data imports (Berkeley, San Francisco)
- Additional demographic sources (daytime population, driving-age, etc.)

## Tech stack

- **Language**: Python (data processing, API)
- **Database**: PostgreSQL (psycopg 3, psycopg-pool)
- **Web**: FastAPI + Jinja2 + htmx (server-rendered HTML with dynamic updates)
- **Charts**: Chart.js (vendored UMD bundle)
- **Build**: Make (HRDAG-style Makefiles), uv (Python deps)
- **Data formats**: XLSX (raw from DOJ), Parquet (intermediate), Postgres (final)

## Development conventions

- Keep tasks small and focused
- Write Makefiles so `make` in any task dir reproduces its outputs
- Commit code and config only; keep data out of the repo
- Use `.gitignore` to exclude `output/`, `input/` data files, etc.
