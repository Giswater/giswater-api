"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import os
from contextlib import asynccontextmanager
from importlib.metadata import version as pkg_version
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import global_settings
from .dependencies import require_feature
from .exceptions import (
    DatabaseUnavailableError,
    ProcedureError,
    database_unavailable_error_handler,
    procedure_error_handler,
)
from .logging import request_logging_middleware
from .models.util_models import GwErrorResponse
from .routers import admin, system
from .routers.basic import basic
from .routers.crm import crm
from .routers.epa import dscenario
from .routers.om import flow, mincut, profile, waterbalance
from .routers.om.mapzones import dma, dqa, omunit, omzone, presszone, sector
from .routers.routing import routing
from .tenant import TenantRegistry
from .tenant_middleware import tenant_middleware
from .utils import utils

TITLE = "Giswater API"
VERSION = pkg_version("giswater-api")
DESCRIPTION = "API for interacting with a Giswater database."


@asynccontextmanager
async def lifespan(app: FastAPI):
    tenants_dir = Path(global_settings.tenants_dir).resolve()
    registry = TenantRegistry(tenants_dir)
    summary = await registry.load_all()
    if registry.is_empty():
        listing = sorted(p.name for p in tenants_dir.iterdir()) if tenants_dir.exists() else "<missing>"
        raise RuntimeError(
            "No tenants loaded; aborting startup. "
            f"tenants_dir={tenants_dir} cwd={os.getcwd()} entries={listing} "
            f"errors={summary.get('errors')}"
        )
    if summary.get("errors"):
        print(f"Tenant load errors: {summary['errors']}")
    print(f"Loaded tenants from {tenants_dir}: {registry.ids()}")

    app.state.registry = registry
    app.state.global_logger = utils.create_log("api", os.path.join(global_settings.log_dir, "_global"))

    try:
        yield
    finally:
        await registry.close_all()


app = FastAPI(
    version=VERSION,
    title=TITLE,
    description=DESCRIPTION,
    root_path=global_settings.root_path,
    responses={
        500: {"model": GwErrorResponse, "description": "Database function error"},
        503: {"model": GwErrorResponse, "description": "Database unavailable"},
    },
    lifespan=lifespan,
)

# Middleware order: Starlette runs registered middlewares in LIFO order.
# Register tenant middleware FIRST so it runs second (inner).
# Register logging middleware LAST so it runs first (outer) and sees every
# response, including 404s emitted by tenant_middleware.
app.middleware("http")(tenant_middleware)
app.middleware("http")(request_logging_middleware)

app.add_exception_handler(ProcedureError, procedure_error_handler)  # type: ignore
app.add_exception_handler(DatabaseUnavailableError, database_unavailable_error_handler)  # type: ignore

# Static files (global)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers: included unconditionally; per-tenant feature gating happens in the
# router-level dependency.
app.include_router(basic.router, dependencies=[Depends(require_feature("api_basic"))])
app.include_router(profile.router, dependencies=[Depends(require_feature("api_profile"))])
app.include_router(flow.router, dependencies=[Depends(require_feature("api_flow"))])
app.include_router(mincut.router, dependencies=[Depends(require_feature("api_mincut"))])
app.include_router(waterbalance.router, dependencies=[Depends(require_feature("api_water_balance"))])
for r in (dma.router, sector.router, presszone.router, dqa.router, omzone.router, omunit.router):
    app.include_router(r, dependencies=[Depends(require_feature("api_mapzones"))])
app.include_router(routing.router, dependencies=[Depends(require_feature("api_routing"))])
app.include_router(crm.router, dependencies=[Depends(require_feature("api_crm"))])
app.include_router(dscenario.router, dependencies=[Depends(require_feature("api_epa"))])

# Tenant-scoped system endpoints (/ready, /logs, /logs/db, /logs/ui, /schemas)
app.include_router(system.router)

# Admin endpoints (/admin/*) — global, no tenant context required
app.include_router(admin.router)

utils.load_plugins(app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "Accepted", "message": f"{TITLE} is running.", "version": VERSION, "description": DESCRIPTION}


@app.get("/health")
async def health():
    """Liveness probe: process is up."""
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint."""
    favicon_path = os.path.join("app", "static", "favicon.ico")
    return FileResponse(favicon_path)
