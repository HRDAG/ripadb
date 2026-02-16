.PHONY: all clean

all: output/done

output/done: src/download.py hand/urls.yaml
	uv run src/download.py --urls hand/urls.yaml --output output
	touch $@

clean:
	rm -rf output/*
