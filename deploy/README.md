# Deployment

ripadb is deployed to a DigitalOcean droplet accessible via SSH as `hrdag0`.
The API runs as a dedicated `ripadb` system user behind an nginx reverse proxy
at `/ripa`.

## Prerequisites on the remote server

- PostgreSQL installed with a `ripadb` database
- `uv` installed for the `ripadb` user (setup script handles this)
- nginx configured to reverse proxy to `127.0.0.1:8001`
- SSH access configured (e.g. `~/.ssh/config` entry for `hrdag0`)

## First-time setup

The setup script handles creating the system user, cloning the repo, granting
Postgres access, and installing the systemd service. SSH into the server and
run:

```bash
sudo bash /path/to/setup-server.sh <repo-url>
```

Or copy it to the server first:

```bash
scp deploy/setup-server.sh hrdag0:/tmp/
ssh hrdag0 sudo bash /tmp/setup-server.sh <repo-url>
```

This script:

1. Creates a `ripadb` system user (no login shell, home at `/var/lib/ripadb`)
2. Clones the repo to `/opt/ripadb`
3. Creates a `ripadb` Postgres role with read-only access to the database
4. Writes `/etc/ripadb/env` with `DATABASE_URL` (readable only by `ripadb`)
5. Installs `uv` for the `ripadb` user
6. Installs and enables the systemd service

### What the setup configures

- **System user**: `ripadb` (no shell, home at `/var/lib/ripadb`)
- **Code location**: `/opt/ripadb` (owned by `ripadb:ripadb`)
- **Database access**: Postgres role `ripadb` with SELECT-only grants via
  peer auth (the Unix user `ripadb` authenticates as Postgres role `ripadb`)
- **Environment**: `/etc/ripadb/env` contains `DATABASE_URL=dbname=ripadb`
- **Hardening**: `NoNewPrivileges`, `ProtectHome`, `ProtectSystem=strict`,
  `PrivateTmp`, `ReadOnlyPaths=/opt/ripadb`

## Deploying

From the local machine, run:

```bash
make deploy
```

This does three things:

1. `git pull` on `hrdag0` (as root, then chowns to `ripadb`)
2. Streams `pg_dump` from local Postgres into `pg_restore` on `hrdag0` (no
   intermediate file)
3. Restarts the `ripadb-api` systemd service (`uv run` resolves deps on start)

To override defaults:

```bash
make deploy REMOTE_HOST=other-server REMOTE_DIR=/other/path DB_NAME=ripadb_test
```

## Managing the service

```bash
# View status
ssh hrdag0 sudo systemctl status ripadb-api

# Tail logs
ssh hrdag0 journalctl -u ripadb-api -f

# Restart manually
ssh hrdag0 sudo systemctl restart ripadb-api

# Stop
ssh hrdag0 sudo systemctl stop ripadb-api
```

## Service configuration

The systemd unit file is `deploy/ripadb-api.service`. Key settings:

- Runs as system user `ripadb` (no shell, minimal privileges)
- Binds to `127.0.0.1:8001` (nginx handles public traffic)
- Auto-restarts on failure (5s delay)
- Environment loaded from `/etc/ripadb/env`
- Systemd hardening directives enabled

If you change the service file, reload on the server:

```bash
ssh hrdag0 sudo systemctl daemon-reload
ssh hrdag0 sudo systemctl restart ripadb-api
```

## Postgres peer auth

The `ripadb` system user authenticates to Postgres via peer auth (Unix user
matches Postgres role). If your `pg_hba.conf` doesn't allow this by default,
add:

```
local   ripadb   ripadb   peer
```

Then `sudo systemctl reload postgresql`.
