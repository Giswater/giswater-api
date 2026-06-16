# Architecture

This service is a multi-tenant FastAPI application. Business logic lives in the
Giswater database (`gw_fct_*` functions); the **service layer** marshals requests
to those functions, while the HTTP and CLI layers stay thin wrappers around the
same services. The layout follows the
[FastAPI "Bigger Applications"](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
conventions and the [full-stack template](https://github.com/fastapi/full-stack-fastapi-template)
(`schemas/` = Pydantic; there is no SQLAlchemy `models/` layer).

## Package map

```
app/
  main.py                 # lifespan, the three FastAPI sub-apps, mounts, middleware + handler registration
  api/                    # HTTP layer (uses absolute `from app...` imports)
    deps.py               # common_parameters / CommonsDep, get_schema, require_feature
    http_errors.py        # map_service_error (domain exceptions -> HTTPException)
    v1/
      router.py           # ROUTER_FEATURES wiring + per-tenant OpenAPI filter
      endpoints/          # thin route handlers; delegate to services/
    admin/
      router.py           # aggregates the admin sub-app routers
      tenants.py          # tenant lifecycle endpoints
      users.py            # gwapi user CRUD endpoints
  services/               # HTTP-agnostic business logic (shared by API + CLI)
    context.py            # ServiceContext, service_context_from_commons
    procedure.py          # run_procedure, ensure_procedure_accepted helpers
    admin/                # tenant_service, user_service
    basic_service.py      # basic GIS endpoints
    crm_service.py        # hydrometer CRUD
    om/                   # flow, profile, mincut, dma, mapzones, waterbalance
    epa/                  # dscenario_service
    routing_service.py
    system_service.py
  cli/                    # Click CLI (`giswater-api` console script)
    bootstrap.py          # tenant registry bootstrap, run_service helper
    main.py               # command groups (admin, tenant)
  core/                   # LEAF: no intra-app imports
    config.py             # GlobalSettings / TenantSettings, AUTH_MODES, deprecation constants
    constants.py          # API_ROOT, TENANT_PREFIX, ADMIN_PREFIX, STATIC_PREFIX, GLOBAL_HEALTH_PATH
    exceptions.py         # ProcedureError, DatabaseUnavailableError + handlers
  auth/
    __init__.py           # re-exports get_current_user, verify_admin, require_role, ApiUser
    session.py            # token verification, get_current_user, require_role, verify_admin
    keycloak.py           # per-tenant Keycloak IDP builder
    users.py              # basic-auth verification + gwapi user store/bootstrap
    schemas.py            # ApiUser + gwapi user DTOs (Pydantic)
    constants.py          # MIN_PASSWORD_LENGTH
  db/
    manager.py            # DatabaseManager (connection pool, schema validation)
    context.py            # DbIdentity, DB_IDENTITY_CTX, REQUEST_ID_CTX, identity resolution
    execution.py          # execute_procedure, execute_sql*
    version.py            # get_db_version (DB query)
    log_store.py          # insert_api_log, insert_api_db_log
    bootstrap/            # DDL bootstrap: __init__ (ensure_tenant_schemas), log.py, gwapi.py
  tenancy/
    registry.py           # Tenant + TenantRegistry
    state.py              # process-global registry / global_logger
    host_middleware.py    # Host header -> tenant resolution
  middleware/
    request_logging.py    # HTTP request logging middleware
  schemas/                # Pydantic request/response models (basic/ crm/ om/ routing/ epa/, admin.py, common.py)
  utils/                  # dependency-light helpers (no DB imports)
    body.py               # create_body_dict, create_api_response, handle_procedure_result
    version.py            # pure version string comparison
    rate_limit.py         # create_rate_limiter
    plugins.py            # load_plugins
    log_setup.py          # create_log, remove_handlers
    routing.py            # Valhalla routing helpers
  static/                 # favicon, logs UI assets
```

## Dependency direction

```
core  <-  everything            (core imports nothing from app)
db / auth / tenancy / schemas / utils  <-  api / middleware / main
```

Rules that keep this acyclic:

- **`core` is a leaf.** It must not import from any other `app.*` package. This is
  why `AUTH_MODES` and `DEPRECATED_KEYCLOAK_ENABLED_ISSUE` live in `core/config.py`
  rather than under `auth/` (a `core.config -> auth -> core.config` cycle otherwise).
- **`db/__init__.py` is empty** (no eager imports), so importing a `db` submodule
  never drags in the whole package.
- The only `db -> auth` edge (`db/bootstrap` bootstrapping the first gwapi user)
  is a **function-local import** inside `ensure_tenant_schemas`, not a module-level one.
- The `api/` layer uses **absolute imports** (`from app.schemas... import ...`);
  shared layers (`core`, `auth`, `db`, `tenancy`, `utils`, `middleware`) use
  relative imports among themselves.

## Where to add code

| Task | Location |
| --- | --- |
| New tenant endpoint | Add handler in `app/api/v1/endpoints/`, implement logic in `app/services/`, wire in `app/api/v1/router.py` `ROUTER_FEATURES` |
| New admin endpoint | `app/api/admin/` + `app/services/admin/` + include in `app/api/admin/router.py` |
| New CLI command | `app/cli/main.py` (call the same service the route uses) |
| New request/response model | `app/schemas/<domain>/` (or `schemas/common.py` for shared) |
| New shared FastAPI dependency | `app/api/deps.py` |
| Shared procedure/body execution | `app/services/procedure.py`, `app/utils/body.py` |
| DB function call / raw SQL helper | `app/db/execution.py` |
| New DDL bootstrap | `app/db/bootstrap/` |
| New config/env var | `app/core/config.py` (+ `docs/ENVIRONMENT_VARIABLES.md`) |
| New auth mode / role logic | `app/auth/` |
| Pure helper (no DB) | `app/utils/` |

## Request lifecycle (tenant API)

1. `host_middleware` resolves the `Host` header to a `Tenant` and stores it on `request.state`.
2. `request_logging` assigns a request id and records the HTTP log entry.
3. `api/deps.py` builds `CommonsDep` (auth identity, schema, DB identity context).
4. The route builds a `ServiceContext` and calls the domain service.
5. The service calls `db/execution.py` (`execute_procedure` / `execute_sql*`), which
   runs the Giswater DB function under the resolved role and optionally writes a DB log.

The same services are available from the CLI (`giswater-api`) for operator scripts.

## Versioning

See [VERSIONING.md](VERSIONING.md).
