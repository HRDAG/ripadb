# ripadb — Project Checklist

## Individual datasets

### RIPA-statewide
- [x] Download stop data (2018-2024, 7 years of XLSX)
- [x] Download board annual reports (2018-2026, 55 files)
- [x] Clean and normalize stop data (235-col union schema, 7 Parquet files, ~26.3M rows)
- [ ] Clean/parse board report tables

### RIPA jurisdiction-specific (planned)
- [ ] RIPA-Berkeley
- [ ] RIPA-San-Francisco
- [ ] Others as identified / PRA responses received

### Supplementary datasets (planned)
- [ ] Census (daytime/nighttime demographics)
- [ ] Arrests
- [ ] Use-of-force
- [ ] Court outcomes
- [ ] CAD logs (via PRA)
- [ ] Calls for service

## Infrastructure
- [x] Repo scaffolding (`.gitignore`, Makefiles, `pyproject.toml`)
- [ ] `match/` — dataset linking
- [ ] **`database/` — Postgres schema, loading, indexes** ← next
- [ ] **`api/` — query server**
- [ ] **`ui/` — agency explorer (MVP)**


## Analyses (planned)
- [ ] Stop outcome analysis (linked arrest/UoF/court data)
- [ ] Pretextual stop ban impact (diff-in-diff: SF, LAPD)
- [ ] Consent search request/refusal rates (2024+ data)
- [ ] Hierarchical modeling of disparities across jurisdictions
- [ ] CAD comparison (underreporting detection)
- [ ] Fraud detection (anomalous reporting patterns)

## Notes

- Data from DOJ is XLSX (not CSV) — one file per county/agency per year
- Coverage: 8 agencies in 2018, all 58 counties + CHP by 2022-2024
- Large agencies (LA, CHP) split into quarterly files
- ~7.9 GB of ZIPs, 270 XLSX files total across 7 years
