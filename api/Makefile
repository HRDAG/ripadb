.PHONY: all run

all: run

# Set ROOT_PATH for reverse proxy deployment, e.g.: make run ROOT_PATH=/ripa
ROOT_PATH ?=

run:
	ROOT_PATH=$(ROOT_PATH) uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
