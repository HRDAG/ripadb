.PHONY: all clean

all: output/acs5_b03002.parquet

output/acs5_b03002.parquet: src/fetch_acs.py
	mkdir -p output
	uv run src/fetch_acs.py --vintage 2023 --output $@

clean:
	rm -rf output/*
