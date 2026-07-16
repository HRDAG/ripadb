.PHONY: all load load-demographics refresh clean

CLEAN_OUTPUT := ../individual/RIPA-statewide/clean/output
DEMOGRAPHICS := ../match/ori-demographics/output/agency_demographics.parquet

all: load

load: src/load.py src/schema.sql
	uv run src/load.py --input $(CLEAN_OUTPUT) --schema src/schema.sql

load-demographics: src/load_demographics.py $(DEMOGRAPHICS)
	uv run src/load_demographics.py --input $(DEMOGRAPHICS)

refresh:
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year;"
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_race;"
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_gender;"
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_age;"
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_race_equip;"

clean:
	psql ripadb -c "DROP MATERIALIZED VIEW IF EXISTS mv_agency_year, mv_agency_year_age, mv_agency_year_gender, mv_agency_year_race, mv_agency_year_race_equip CASCADE;"
	psql ripadb -c "DROP TABLE IF EXISTS jurisdiction_demographics, stops, agencies, rae_labels, gender_labels, reason_labels, age_group_labels CASCADE;"
