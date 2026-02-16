.PHONY: all clean

all: output/data

output/data: src/download.py hand/urls.yaml
	mkdir -p output/zip output/data output/readme
	uv run src/download.py --urls hand/urls.yaml --output output

clean:
	rm -rf output/*
