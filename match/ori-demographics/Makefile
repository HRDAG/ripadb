.PHONY: all clean build-crosswalk

ACS_DATA := ../../individual/census/fetch/output/acs5_b03002.parquet

all: output/agency_demographics.parquet

# One-time: generate crosswalk for manual review
build-crosswalk: src/build_crosswalk.py
	mkdir -p output
	uv run src/build_crosswalk.py --output output/crosswalk.yaml

# Main target: join crosswalk with ACS data
output/agency_demographics.parquet: src/join_demographics.py hand/crosswalk.yaml $(ACS_DATA)
	mkdir -p output
	uv run src/join_demographics.py \
		--crosswalk hand/crosswalk.yaml \
		--acs $(ACS_DATA) \
		--source acs5_2023_residential \
		--output $@

clean:
	rm -rf output/*
