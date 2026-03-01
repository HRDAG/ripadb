.PHONY: all build run

all: run

# Set ROOT_PATH for reverse proxy deployment, e.g.: make run ROOT_PATH=/ripa
ROOT_PATH ?=

build:
	uv run python -m src.build_articles

run: build
	ROOT_PATH=$(ROOT_PATH) uv run uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
