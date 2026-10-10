# Census Gazetteer: land area + internal point (lat/lon) for CA places
# (incorporated cities + CDPs) and counties.
# https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html

VINTAGE := 2024
BASE := https://www2.census.gov/geo/docs/maps-data/data/gazetteer/$(VINTAGE)_Gazetteer

.PHONY: all clean

all: output/ca_places.parquet output/ca_counties.parquet

output/raw/$(VINTAGE)_gaz_%_06.txt:
	mkdir -p output/raw
	curl -sSf -o $@ $(BASE)/$(notdir $@)

output/ca_places.parquet: src/parse_gazetteer.py output/raw/$(VINTAGE)_gaz_place_06.txt
	mkdir -p output
	uv run src/parse_gazetteer.py --input output/raw/$(VINTAGE)_gaz_place_06.txt --output $@

output/ca_counties.parquet: src/parse_gazetteer.py output/raw/$(VINTAGE)_gaz_counties_06.txt
	mkdir -p output
	uv run src/parse_gazetteer.py --input output/raw/$(VINTAGE)_gaz_counties_06.txt --output $@

clean:
	rm -rf output/*
