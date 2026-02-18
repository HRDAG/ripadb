.PHONY: all load refresh clean

CLEAN_OUTPUT := ../individual/RIPA-statewide/clean/output

all: load

load: src/load.py src/schema.sql
	uv run src/load.py --input $(CLEAN_OUTPUT) --schema src/schema.sql

refresh:
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_race;"
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_gender;"
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_age;"
	psql ripadb -c "REFRESH MATERIALIZED VIEW mv_agency_year_race_equip;"

clean:
	psql ripadb -c "DROP MATERIALIZED VIEW IF EXISTS mv_agency_year_age, mv_agency_year_gender, mv_agency_year_race, mv_agency_year_race_equip CASCADE;"
	psql ripadb -c "DROP TABLE IF EXISTS stops, agencies, rae_labels, gender_labels, reason_labels, age_group_labels CASCADE;"
