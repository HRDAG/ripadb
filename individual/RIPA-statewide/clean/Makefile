.PHONY: all clean

STOPS := ../download-stops/output/data
YEARS := 2018 2019 2020 2021 2022 2023 2024

all: $(patsubst %,output/%.parquet,$(YEARS))

output/%.parquet: src/clean.py hand/schema.yaml $(STOPS)/%
	mkdir -p output
	uv run src/clean.py --year $* \
		--input $(STOPS)/$* \
		--schema hand/schema.yaml \
		--output $@

clean:
	rm -rf output/*
