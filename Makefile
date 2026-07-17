.PHONY: all individual deploy

REMOTE_HOST ?= hrdag0
REMOTE_DIR  ?= /opt/ripadb
DB_NAME     ?= ripadb

all: individual

individual:
	$(MAKE) -C $@

deploy:
	@echo "==> Pulling latest code on $(REMOTE_HOST)..."
	ssh $(REMOTE_HOST) "git -C $(REMOTE_DIR) pull"
	@echo "==> Streaming database to $(REMOTE_HOST)..."
	pg_dump -Fc $(DB_NAME) | ssh $(REMOTE_HOST) "pg_restore --clean --if-exists -d $(DB_NAME)"
	@echo "==> Restarting API on $(REMOTE_HOST)..."
	ssh $(REMOTE_HOST) "sudo systemctl restart ripadb-api"
	@echo "==> Deploy complete."
