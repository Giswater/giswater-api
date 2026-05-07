"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging
import os
from collections.abc import Callable
from contextlib import asynccontextmanager
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.routing import BaseRoute

from . import state
from .auth import verify_admin
from .config import global_settings
from .constants import ADMIN_PREFIX, TENANT_PREFIX
from .dependencies import require_feature
from .exceptions import (
    DatabaseUnavailableError,
    ProcedureError,
    database_unavailable_error_handler,
    procedure_error_handler,
)
from .host_middleware import host_middleware
from .logging import request_logging_middleware
from .models.util_models import GwErrorResponse
from .routers import admin, system
from .routers.basic import basic
from .routers.crm import crm
from .routers.epa import dscenario
from .routers.om import flow, mincut, profile, waterbalance
from .routers.om.mapzones import dma, dqa, omunit, omzone, presszone, sector
from .routers.routing import routing
from .tenant import Tenant, TenantRegistry
from .utils import utils

TITLE = "Giswater API"
VERSION = pkg_version("giswater-api")
DESCRIPTION = "API for interacting with a Giswater database."
logger = logging.getLogger(__name__)

# Tuple list: `APIRouter` is not hashable in Python 3.13+ (cannot use as dict keys).
ROUTER_FEATURES: list[tuple[APIRouter, str]] = [
    (basic.router, "api_basic"),
    (profile.router, "api_profile"),
    (flow.router, "api_flow"),
    (mincut.router, "api_mincut"),
    (waterbalance.router, "api_water_balance"),
    (routing.router, "api_routing"),
    (crm.router, "api_crm"),
    (dscenario.router, "api_epa"),
    (dma.router, "api_mapzones"),
    (sector.router, "api_mapzones"),
    (presszone.router, "api_mapzones"),
    (dqa.router, "api_mapzones"),
    (omzone.router, "api_mapzones"),
    (omunit.router, "api_mapzones"),
]

# Map endpoint callables to feature flag — used for per-tenant OpenAPI filtering.
FEATURE_BY_ENDPOINT: dict[Callable[..., Any], str] = {}
for _rtr, _flag in ROUTER_FEATURES:
    for _route in _rtr.routes:
        ep = getattr(_route, "endpoint", None)
        if callable(ep):
            FEATURE_BY_ENDPOINT[ep] = _flag


def _tenant_openapi_routes(tenant: Tenant) -> list[BaseRoute]:
    """Routes to expose in OpenAPI for this tenant (feature toggles)."""
    out: list[BaseRoute] = []
    for route in tenant_app.routes:
        ep = getattr(route, "endpoint", None)
        flag = FEATURE_BY_ENDPOINT.get(ep) if callable(ep) else None
        if flag is None or getattr(tenant.settings, flag, False):
            out.append(route)
    return out


def _register_health_route(app: FastAPI) -> None:
    @app.get("/health", include_in_schema=False)
    async def health():
        """Liveness probe: process is up."""
        return {"status": "ok"}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    tenants_dir = Path(global_settings.tenants_dir).resolve()
    registry = TenantRegistry(tenants_dir)
    summary = await registry.load_all()
    if registry.is_empty():
        listing = sorted(p.name for p in tenants_dir.iterdir()) if tenants_dir.exists() else "<missing>"
        logger.warning(
            "No tenants loaded at startup (admin can create tenants). tenants_dir=%s cwd=%s entries=%s errors=%s",
            tenants_dir,
            os.getcwd(),
            listing,
            summary.get("errors"),
        )
    elif summary.get("errors"):
        logger.warning("Tenant load errors: %s", summary["errors"])
    if not registry.is_empty():
        logger.info("Loaded tenants from %s: %s", tenants_dir, registry.ids())

    state.registry = registry
    state.global_logger = utils.create_log("api", os.path.join(global_settings.log_dir, "_global"))

    try:
        yield
    finally:
        await registry.close_all()
        state.registry = None
        state.global_logger = None


parent = FastAPI(
    version=VERSION,
    title=TITLE,
    description=DESCRIPTION,
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
    lifespan=lifespan,
    responses={
        500: {"model": GwErrorResponse, "description": "Database function error"},
        503: {"model": GwErrorResponse, "description": "Database unavailable"},
    },
)

tenant_app = FastAPI(
    version=VERSION,
    title=TITLE,
    description=DESCRIPTION,
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
    responses={
        500: {"model": GwErrorResponse, "description": "Database function error"},
        503: {"model": GwErrorResponse, "description": "Database unavailable"},
    },
)

for _router, _flag in ROUTER_FEATURES:
    tenant_app.include_router(_router, dependencies=[Depends(require_feature(_flag))])
tenant_app.include_router(system.router)


@tenant_app.get("/", summary="Service status")
async def tenant_root():
    return {
        "status": "Accepted",
        "message": f"{TITLE} is running.",
        "version": VERSION,
        "description": DESCRIPTION,
    }


@tenant_app.get("/openapi.json", include_in_schema=False)
async def tenant_openapi_json(request: Request):
    tenant: Tenant = request.state.tenant
    routes = _tenant_openapi_routes(tenant)
    root_path = request.scope.get("root_path") or TENANT_PREFIX
    schema = get_openapi(
        title=TITLE,
        version=VERSION,
        description=DESCRIPTION,
        routes=routes,
        servers=[{"url": root_path}],
    )
    return JSONResponse(schema)


@tenant_app.get("/docs", include_in_schema=False)
async def tenant_docs():
    return get_swagger_ui_html(
        openapi_url=f"{TENANT_PREFIX}/openapi.json",
        title=f"{TITLE} - docs",
    )


@tenant_app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join("app", "static", "favicon.ico")
    return FileResponse(favicon_path)


admin_app = FastAPI(
    title=f"{TITLE} - Admin",
    version=VERSION,
    description="Platform admin API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    dependencies=[Depends(verify_admin)],
    responses={
        500: {"model": GwErrorResponse, "description": "Database function error"},
        503: {"model": GwErrorResponse, "description": "Database unavailable"},
    },
)
admin_app.include_router(admin.router)

parent.mount(ADMIN_PREFIX, admin_app)
parent.mount(TENANT_PREFIX, tenant_app)
parent.mount("/static", StaticFiles(directory="app/static"), name="static")

for _app in (parent, tenant_app, admin_app):
    _register_health_route(_app)


# Middleware order: Starlette runs LIFO — register host_middleware first so it runs inner.
parent.middleware("http")(host_middleware)
parent.middleware("http")(request_logging_middleware)

for _app in (parent, tenant_app, admin_app):
    _app.add_exception_handler(ProcedureError, procedure_error_handler)  # type: ignore[arg-type]
    _app.add_exception_handler(DatabaseUnavailableError, database_unavailable_error_handler)  # type: ignore[arg-type]

utils.load_plugins(tenant_app)

app = parent
