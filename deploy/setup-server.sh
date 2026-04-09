#!/usr/bin/env bash
# First-time server setup for ripadb API.
# Run as root (or with sudo) on the remote server.
set -euo pipefail

REPO_URL="${1:?Usage: $0 <git-repo-url>}"
INSTALL_DIR=/opt/ripadb
DB_NAME=ripadb

echo "==> Creating ripadb system user..."
if ! id ripadb &>/dev/null; then
    useradd -r -s /usr/sbin/nologin -d "$INSTALL_DIR" ripadb
fi

echo "==> Cloning repo to $INSTALL_DIR..."
if [ ! -d "$INSTALL_DIR/.git" ]; then
    git clone "$REPO_URL" "$INSTALL_DIR"
else
    echo "    (already cloned, pulling latest)"
    git -C "$INSTALL_DIR" pull
fi
chown -R ripadb:ripadb "$INSTALL_DIR"

echo "==> Creating Postgres role and granting access..."
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='ripadb'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE ROLE ripadb LOGIN;"
fi
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE $DB_NAME TO ripadb;"
sudo -u postgres psql -d "$DB_NAME" -c "GRANT USAGE ON SCHEMA public TO ripadb;"
sudo -u postgres psql -d "$DB_NAME" -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO ripadb;"
sudo -u postgres psql -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ripadb;"

echo "==> Setting up environment file..."
mkdir -p /etc/ripadb
cat > /etc/ripadb/env <<EOF
DATABASE_URL="dbname=$DB_NAME"
EOF
chmod 640 /etc/ripadb/env
chown root:ripadb /etc/ripadb/env

echo "==> Creating Python virtualenv..."
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -r "$INSTALL_DIR/deploy/requirements.txt"
chown -R ripadb:ripadb "$INSTALL_DIR/.venv"

echo "==> Installing systemd service..."
ln -sf "$INSTALL_DIR/deploy/ripadb-api.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now ripadb-api

echo "==> Done. Check status with: systemctl status ripadb-api"
