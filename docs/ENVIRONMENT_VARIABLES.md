# Environment variables

This document is the **reference** for all configuration keys. For a **copy-paste template** of current defaults, use [`.env.example`](../.env.example) (process-wide) and [`config/tenants/example.env`](../config/tenants/example.env) (per tenant).

| Where | File | Loaded by |
| ----- | ---- | --------- |
| Process (global) | `.env` at project root | `load_dotenv()` in [`app/config.py`](../app/config.py) |
| Per tenant | `config/tenants/<tenant_id>.env` | `dotenv_values()` only (does not pollute `os.environ`) |

Boolean env vars accept: `true`, `t`, `yes`, `y`, `1`, `on` (case-insensitive). Empty or unset uses the **default** shown below.

---

## Process-wide (`.env`)

These apply to the whole Python process: routing, logging, admin API, platform Keycloak, and (when using the production Docker image) Gunicorn.

### Routing

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `BASE_DOMAIN` | `bgeo360.com` | Apex domain: the bare host (`BASE_DOMAIN`) serves `/admin/*`; `tenant.BASE_DOMAIN` serves `/gw-api/v1/*`. Tenant id is the leftmost DNS label (subdomain). |
| `TENANTS_DIR` | `config/tenants` | Directory containing one `\<id\>.env` per tenant. Files named `example.env`, `sample.env`, `template.env` are ignored for discovery. |

### Logging

Request logging writes JSON lines to rotating files under `LOG_DIR`, and optionally inserts sampled rows into the tenant database API log table.

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `LOG_LEVEL` | `INFO` | Root logging level for handlers created via `create_log` (e.g. `DEBUG`, `INFO`, `WARNING`). |
| `LOG_DIR` | `logs` | Base directory for API log files (`\<LOG_DIR\>/\<tenant_or_global\>/\<YYYYMMDD\>/`). |
| `LOG_ROTATE_DAYS` | `14` | Number of rotated daily log files to retain. |
| `LOG_DB_ENABLED` | `true` | When `true`, eligible tenant requests may insert rows into the tenant DB API log schema (subject to sample rate). |
| `LOG_DB_SAMPLE_RATE` | `1.0` | Fraction (0–1) of tenant-scoped requests that pass random sampling for **DB** log inserts. `1.0` means every eligible request is considered (typical for QGIS plugin traffic). `0` turns off DB sampling together with `LOG_DB_ENABLED` logic; prefer `LOG_DB_ENABLED=false` to disable DB logging entirely. Lower the rate if the log table becomes a bottleneck. |
| `LOG_HTTP_BODY_CAPTURE` | `true` | When `true`, request/response **payload text** is included in log records (still truncated). When `false`, only metadata (sizes, timing, allowlisted headers, etc.)—useful for strict data-minimization. |
| `LOG_DB_MAX_BODY_BYTES` | `2048` | Max bytes stored per request/response body when capture is on. `0` uses an internal safe cap (same as 2048-style limit). |

### Giswater DB compatibility (readiness)

Used only when evaluating tenant **`GET /gw-api/v1/ready`** (after the database is reachable).

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `GISWATER_DB_VERSION_CHECK` | `false` | When `true`, readiness compares `{DB_SCHEMA}.sys_version.giswater` to `GISWATER_DB_MIN_VERSION`. Returns **503** if missing or below minimum. |
| `GISWATER_DB_MIN_VERSION` | `4.8.0` | Minimum Giswater DB version string for the check (parsed as dotted numeric components). Align with [README compatibility](../README.md#compatibility). |

### Rate limiting

Applied by dependencies on selected routes (see [`app/utils/utils.py`](../app/utils/utils.py) `create_rate_limiter`).

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `RATE_LIMIT_DEFAULT_MAX_REQUESTS` | `30` | Max requests per client IP per window for default-scoped limiters. |
| `RATE_LIMIT_DEFAULT_WINDOW_SECONDS` | `60` | Sliding window length in seconds. Set `max_requests` or `window_seconds` ≤ `0` in code contexts that honor those knobs to disable (see usages). |

### Admin API (`/admin/*`)

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `ADMIN_USER` | `admin` | HTTP Basic user for admin routes. Legacy alias: `LOG_ADMIN_USER`. |
| `ADMIN_PASSWORD` | _(empty)_ | HTTP Basic password; leave unset only in trusted dev environments. Legacy alias: `LOG_ADMIN_PASSWORD`. |
| `ADMIN_RELOAD_ENABLED` | `true` | When `false`, directory-wide tenant reload is refused (gate for `POST /admin/tenants/reload`). |
| `ADMIN_WRITE_ENABLED` | `true` | When `false`, tenant create/update/delete and single-tenant reload mutations are refused. |
| `ADMIN_ARCHIVE_ON_DELETE` | `true` | When `true`, deleting a tenant moves its `.env` to `TENANTS_DIR/_archive/` instead of unlinking. |

### Development

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `DEV_ALLOW_TENANT_HEADER` | `false` | When `true`, non-apex hosts may send `X-Tenant-ID` to pick a tenant without DNS-based host matching (local/dev only). |

### Platform Keycloak (admin Bearer auth)

Separate from **per-tenant** Keycloak. Used to validate **`Authorization: Bearer`** on `/admin/*` when enabled. Required realm role: **`platform-admin`**. HTTP Basic (`ADMIN_*`) can still be used in parallel.

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `PLATFORM_KEYCLOAK_ENABLED` | `false` | Master switch for JWT validation against the platform IdP. |
| `PLATFORM_KEYCLOAK_URL` | _(empty)_ | Keycloak base URL. |
| `PLATFORM_KEYCLOAK_REALM` | _(empty)_ | Realm name. |
| `PLATFORM_KEYCLOAK_CLIENT_ID` | _(empty)_ | Client id used for API/resource validation context. |
| `PLATFORM_KEYCLOAK_CLIENT_SECRET` | _(empty)_ | Client secret when required by your deployment. |

---

## Gunicorn (production Docker image only)

The [`Dockerfile`](../Dockerfile) starts **`gunicorn -c gunicorn.conf.py`**. These variables are read in [`gunicorn.conf.py`](../gunicorn.conf.py). They are **ignored** when you run **`uvicorn --reload`** locally.

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `GUNICORN_BIND` | `0.0.0.0:8000` | `host:port` passed to Gunicorn `bind`. |
| `WEB_CONCURRENCY` | _(auto)_ | Worker count. If unset or invalid, uses `min(2 × CPU + 1, 8)` with at least **1** worker. |
| `GUNICORN_TIMEOUT` | `120` | Worker silent timeout (seconds) before kill/restart. |
| `GUNICORN_GRACEFUL_TIMEOUT` | `30` | Seconds to finish requests after reload/SIGTERM. |
| `GUNICORN_KEEPALIVE` | `5` | HTTP keep-alive seconds. |
| `GUNICORN_MAX_REQUESTS` | `2000` | Restart worker after this many requests (mitigate leaks). |
| `GUNICORN_MAX_REQUESTS_JITTER` | `200` | Random jitter added to `max_requests`. |
| `GUNICORN_ACCESSLOG` | `-` | Access log destination (`-` = stdout). |
| `GUNICORN_ERRORLOG` | `-` | Error log destination (`-` = stderr). |
| `GUNICORN_LOG_LEVEL` | `info` | Gunicorn’s own log level. |
| `GUNICORN_CAPTURE_OUTPUT` | `true` | When true, forward worker stdout/stderr into Gunicorn error log. |

---

## Per-tenant environment files

One file per tenant: `config/tenants/<tenant_id>.env`. The filename stem is the tenant id and must match the subdomain (`acme` → `https://acme.<BASE_DOMAIN>/gw-api/v1/...`).

**Template with inline comments:** [`config/tenants/example.env`](../config/tenants/example.env).

### API feature toggles

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `API_BASIC` | `false` | Basic GIS/feature endpoints module. |
| `API_PROFILE` | `false` | Profile / trace tools module. |
| `API_FLOW` | `false` | Flow analysis endpoints. |
| `API_MINCUT` | `false` | Mincut operations. |
| `API_WATER_BALANCE` | `false` | Water balance endpoints. |
| `API_MAPZONES` | `false` | Mapzones (DMA, sector, etc.). |
| `API_ROUTING` | `false` | External routing (Valhalla) integration. |
| `API_CRM` | `false` | CRM / hydrometer-style endpoints. |
| `API_EPA` | `false` | EPA / dscenario endpoints. |

### Database

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `DB_HOST` | `localhost` | Postgres host. |
| `DB_PORT` | `5432` | Postgres port. |
| `DB_NAME` | `postgres` | Database name. |
| `DB_USER` | `postgres` | Database user. |
| `DB_PASSWORD` | `postgres` | Database password. |
| `DB_SCHEMA` | `public` | Giswater schema for this tenant (functions, `sys_version`, etc.). |
| `DATABASE_URL` | _(optional)_ | If set, overrides individual `DB_*` components for the pool URL (see [`DatabaseManager`](../app/database.py)). |

### Connection pool (per tenant)

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `DB_POOL_MIN_SIZE` | `1` | Pool minimum connections. |
| `DB_POOL_MAX_SIZE` | `10` | Pool maximum connections. Total DB load ≈ **tenants × `DB_POOL_MAX_SIZE`**. |
| `DB_POOL_TIMEOUT` | `30` | Seconds to wait for a connection from the pool. |
| `DB_POOL_MAX_WAITING` | `0` | Max queued waiters (psycopg pool). |
| `DB_POOL_MAX_IDLE` | `300` | Seconds before idle connections may be dropped. |
| `DB_CONNECT_TIMEOUT` | `5` | Seconds for initial pool open / connectivity checks. |

### Keycloak (tenant API)

When **`KEYCLOAK_ENABLED=true`**, tenant routes expect a valid Bearer JWT for that realm. When `false`, anonymous access is allowed for that tenant (still subject to feature toggles).

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `KEYCLOAK_ENABLED` | `false` | Enable JWT enforcement for this tenant’s `/gw-api/v1/*`. |
| `KEYCLOAK_URL` | _(required if enabled)_ | Keycloak base URL. |
| `KEYCLOAK_REALM` | _(required if enabled)_ | Realm. |
| `KEYCLOAK_CLIENT_ID` | _(required if enabled)_ | Client id. |
| `KEYCLOAK_CLIENT_SECRET` | _(required if enabled)_ | Client secret. |
| `KEYCLOAK_ADMIN_CLIENT_ID` | _(required if enabled)_ | Admin client (service account / mgmt). |
| `KEYCLOAK_ADMIN_CLIENT_SECRET` | _(required if enabled)_ | Admin client secret. |
| `KEYCLOAK_CALLBACK_URI` | _(required if enabled)_ | Callback URI registered in Keycloak for this client setup. |

---

## See also

- [`.env.example`](../.env.example) — copy-paste root defaults
- [Deployment checklist](DEPLOYMENT_CHECKLIST.md)
- [README – Configuration](../README.md#configuration)
- [README – Compatibility](../README.md#compatibility)
