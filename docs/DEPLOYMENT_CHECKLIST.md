# Production deployment checklist (v1.0+)

Use with [.env.prod.example](../.env.prod.example), [Environment variables](ENVIRONMENT_VARIABLES.md), and [README.md](../README.md#deployment-notes).

## Before go-live

- [ ] **TLS** terminates at reverse proxy; certificates valid and auto-renewed.
- [ ] **Host routing**: `proxy_set_header Host $host;` (tenant id is the left label of the Host).
- [ ] **Apex vs tenant**: apex `BASE_DOMAIN` → `/admin/*` only; `*.BASE_DOMAIN` → `/gw-api/v1/*`.
- [ ] **Secrets**: `ADMIN_PASSWORD` set; Keycloak secrets not in git; DB password least-privilege.
- [ ] **Postgres**: version matches [compatibility table](../README.md#compatibility); backup/restore tested.
- [ ] **Pool budget**: `N_tenants × DB_POOL_MAX_SIZE` within Postgres `max_connections`.
- [ ] **Logging**: `LOG_DB_SAMPLE_RATE=1.0` for full API request audit; lower if the DB log table becomes hot. Use `LOG_HTTP_BODY_CAPTURE=false` only when you must avoid storing payload text; otherwise bodies are truncated via `LOG_DB_MAX_BODY_BYTES`.
- [ ] **Readiness**: `GISWATER_DB_VERSION_CHECK=true` in prod if you want `/ready` to enforce min Giswater DB (see `GISWATER_DB_MIN_VERSION`).
- [ ] **Gunicorn**: `WEB_CONCURRENCY` set for CPU/RAM; container `start_period` allows pool + DB connect.
- [ ] **Probes**: liveness `GET /health`; readiness per tenant `GET /gw-api/v1/ready` (503 if DB or version check fails).

## Rollout / rollback

- [ ] Tag image / artifact with app version; keep previous image for quick rollback.
- [ ] DB migrations (if any) run in a controlled window; have rollback SQL or restore point.
- [ ] After deploy: [scripts/smoke_test.sh](../scripts/smoke_test.sh) or `pytest` operability test in CI.

## Ongoing

- [ ] **Log retention** and disk for `LOG_DIR` + API log table growth.
- [ ] **Credential rotation** for DB, admin, Keycloak on a defined schedule.
- [ ] **Upgrade path**: read `CHANGELOG.md` and matching Giswater DB release notes before bumping.
