# Daily sun times (civil dawn, sunrise, sunset, civil dusk) for every CA
# Census place and county, for veil-of-darkness analyses.
#
# Times are computed astronomically (astral, NOAA solar position algorithm)
# at each geography's Census internal point, in America/Los_Angeles local
# time (DST-aware, matching RIPA TIME_OF_STOP). Dawn/dusk = civil twilight
# (sun 6 degrees below horizon), as in Pierson et al. 2020 / Stanford OPP.
# validate.py spot-checks a random sample against the US Naval Observatory API.

GAZ := ../gazetteer/output
START := 2018-01-01
END := 2024-12-31

.PHONY: all clean

all: output/sun_times.parquet output/usno_validation.csv

output/sun_times.parquet: src/compute_sun_times.py $(GAZ)/ca_places.parquet $(GAZ)/ca_counties.parquet
	mkdir -p output
	uv run src/compute_sun_times.py --places $(GAZ)/ca_places.parquet \
		--counties $(GAZ)/ca_counties.parquet --start $(START) --end $(END) --output $@

output/usno_validation.csv: src/validate.py output/sun_times.parquet
	uv run src/validate.py --input output/sun_times.parquet --gazetteer $(GAZ) --n 40 --seed 1 --output $@

clean:
	rm -rf output/*
