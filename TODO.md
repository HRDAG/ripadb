# ripadb — Project Checklist

## Overall

- [x] Initialize git repo and CLAUDE.md
- [x] Set up repo scaffolding (`.gitignore`, top-level Makefile, `pyproject.toml`)
- [x] Import pipeline: download RIPA stop data (2018-2024)
- [x] Import pipeline: download RIPA board annual reports (2018-2026)
- [ ] **Clean pipeline: normalize and validate data** ← next
- [ ] Database pipeline: Postgres schema, loading, indexes
- [ ] API: simple query server
- [ ] UI: web-based data explorer
- [ ] Analysis: deeper-than-annual-report analyses

## Notes

- Data from DOJ is XLSX (not CSV) — one file per county/agency per year
- Coverage: 8 agencies in 2018, all 58 counties + CHP by 2022-2024
- Large agencies (LA, CHP) split into quarterly files
- ~7.9 GB of ZIPs, 270 XLSX files total across 7 years
