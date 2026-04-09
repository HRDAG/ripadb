.PHONY: all individual deploy

REMOTE_HOST ?= hrdag0
REMOTE_DIR  ?= /opt/ripadb
DB_NAME     ?= ripadb

all: individual

individual:
	$(MAKE) -C $@

deploy:
	@echo "==> Pulling latest code on $(REMOTE_HOST)..."
	ssh $(REMOTE_HOST) "sudo git -C $(REMOTE_DIR) pull && sudo chown -R ripadb:ripadb $(REMOTE_DIR)"
	@echo "==> Streaming database to $(REMOTE_HOST)..."
	pg_dump -Fc $(DB_NAME) | ssh $(REMOTE_HOST) "pg_restore --clean --if-exists -d $(DB_NAME)"
	@echo "==> Rebuilding virtualenv on $(REMOTE_HOST)..."
	ssh $(REMOTE_HOST) "sudo $(REMOTE_DIR)/.venv/bin/pip install --quiet -r $(REMOTE_DIR)/deploy/requirements.txt && sudo chown -R ripadb:ripadb $(REMOTE_DIR)/.venv"
	@echo "==> Restarting API on $(REMOTE_HOST)..."
	ssh $(REMOTE_HOST) "sudo systemctl restart ripadb-api"
	@echo "==> Deploy complete."
