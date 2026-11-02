# Link RIPA stops to daily sun times (dawn, sunrise, sunset, dusk) at the
# stop location, for veil-of-darkness analyses.
#
# Location = LOC_CLOSEST_CITY resolved to a Census place (or county for
# "UNINCORPORATED AREA-X" and unresolvable names); see
# src/build_city_crosswalk.py for the resolution order. The crosswalk's
# match_method lets analyses restrict to place-level locations.
# Output: one row per stop (DOJ_RECORD_ID) per year.

CLEAN := ../../individual/RIPA-statewide/clean/output
GAZ := ../../individual/census/gazetteer/output
SUN := ../../individual/census/compute-sun-times/output/sun_times.parquet
YEARS := 2018 2019 2020 2021 2022 2023 2024

.PHONY: all clean

all: output/city_crosswalk.parquet $(patsubst %,output/%.parquet,$(YEARS))

output/city_crosswalk.parquet: src/build_city_crosswalk.py hand/city_aliases.yaml \
		$(GAZ)/ca_places.parquet $(GAZ)/ca_counties.parquet \
		$(patsubst %,$(CLEAN)/%.parquet,$(YEARS))
	mkdir -p output
	uv run src/build_city_crosswalk.py --stops '$(CLEAN)/*.parquet' \
		--places $(GAZ)/ca_places.parquet --counties $(GAZ)/ca_counties.parquet \
		--aliases hand/city_aliases.yaml --output $@

output/%.parquet: src/link_sun_times.py output/city_crosswalk.parquet $(SUN) $(CLEAN)/%.parquet
	uv run src/link_sun_times.py --stops $(CLEAN)/$*.parquet \
		--crosswalk output/city_crosswalk.parquet --sun-times $(SUN) --output $@

clean:
	rm -rf output/*
