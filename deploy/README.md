# Production deployment (single-tenant)

Interactive installer for Debian/Ubuntu servers with Docker. Creates `/opt/giswater-api` with:

- `docker-compose.yml` — published image, log volume fix, loopback bind
- `.env` — `SINGLE_TENANT_ID=main`, admin password, image tag
- `config/tenants/main.env` — Postgres + optional Keycloak
- `docker-entrypoint.sh` — ensures `/app/logs` is writable

## Quick start

From any directory on the server:

```bash
curl -fsSL https://raw.githubusercontent.com/Giswater/giswater-api/main/deploy/install.sh | sudo bash
```

Pin a release:

```bash
GISWATER_API_REF=v1.3.2 curl -fsSL https://raw.githubusercontent.com/Giswater/giswater-api/main/deploy/install.sh | sudo bash
```

Or download first:

```bash
wget -O install.sh https://raw.githubusercontent.com/Giswater/giswater-api/main/deploy/install.sh
chmod +x install.sh
sudo GISWATER_API_REF=v1.3.2 ./install.sh
```

## What the installer asks

| Prompt | Purpose |
|--------|---------|
| Public URL / IP | Printed endpoints; default Keycloak callback |
| Docker image tag | `GISWATER_API_TAG` (default `latest`) |
| Admin password | HTTP Basic for `${API_ROOT}/admin/*` |
| DB connection | Host, port, name, user, password, schema |
| Keycloak (optional) | Per-tenant auth for `${API_ROOT}/v1/*` |

When Postgres runs on the same host as Docker, use **`host.docker.internal`** as DB host (default).

## Manual setup

```bash
sudo mkdir -p /opt/giswater-api/config/tenants
cd /opt/giswater-api
# copy deploy/docker-compose.yml, docker-entrypoint.sh,
#       deploy/.env.prod.example → .env,
#       deploy/main.env.example → config/tenants/main.env
# edit secrets, then:
docker compose pull && docker compose up -d
```

## Files

| File | Role |
|------|------|
| [docker-compose.yml](docker-compose.yml) | Production Compose (no local build) |
| [docker-entrypoint.sh](docker-entrypoint.sh) | Fix log volume permissions |
| [.env.prod.example](.env.prod.example) | Root `.env` template |
| [main.env.example](main.env.example) | Single-tenant `main.env` template |
| [nginx.conf.example](nginx.conf.example) | Reverse proxy (single-tenant block at bottom) |
| [install.sh](install.sh) | Interactive installer |

## Upgrade

```bash
cd /opt/giswater-api
# bump GISWATER_API_TAG in .env, or re-run install.sh with GISWATER_API_REF
docker compose pull && docker compose up -d
```

See also [docs/DEPLOYMENT_CHECKLIST.md](../docs/DEPLOYMENT_CHECKLIST.md) and [docs/ENVIRONMENT_VARIABLES.md](../docs/ENVIRONMENT_VARIABLES.md).
