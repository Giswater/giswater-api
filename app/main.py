"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import DatabaseManager
from .keycloak import idp
from .config import settings
from .utils import utils
from .exceptions import ProcedureError, procedure_error_handler
from .routers.basic import basic
from .routers.om import mincut, profile, flow
from .routers.waterbalance import water_balance
from .routers.epa import hydraulic_engine_ud, hydraulic_engine_ws
from .routers.routing import routing
from .routers.crm import crm
from .models.util_models import GwErrorResponse

TITLE = "Giswater API"
VERSION = "0.5.0"
DESCRIPTION = "API for interacting with a Giswater database."

# Database manager
db_manager = DatabaseManager()

# Create FastAPI app
app = FastAPI(
    version=VERSION,
    title=TITLE,
    description=DESCRIPTION,
    root_path="/api/v1",
    responses={500: {"model": GwErrorResponse, "description": "Database function error"}},
)

# Register exception handlers
app.add_exception_handler(ProcedureError, procedure_error_handler)

# Add Keycloak Swagger config if enabled
if idp:
    idp.add_swagger_config(app)

# Store in app.state for access in routes
app.state.settings = settings
app.state.db_manager = db_manager


# Initialize/close async pool on app lifecycle
@app.on_event("startup")
async def startup() -> None:
    await db_manager.init_conn_pool()


@app.on_event("shutdown")
async def shutdown() -> None:
    await db_manager.close()


# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers conditionally based on config
if settings.api_basic:
    app.include_router(basic.router)
if settings.api_profile:
    app.include_router(profile.router)
if settings.api_flow:
    app.include_router(flow.router)
if settings.api_mincut:
    app.include_router(mincut.router)
if settings.api_water_balance:
    app.include_router(water_balance.router)
if settings.api_routing:
    app.include_router(routing.router)
if settings.api_crm:
    app.include_router(crm.router)
if settings.hydraulic_engine_enabled:
    if settings.hydraulic_engine_ud:
        app.include_router(hydraulic_engine_ud.router)
    if settings.hydraulic_engine_ws:
        app.include_router(hydraulic_engine_ws.router)

# Load plugins
utils.load_plugins(app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "Accepted", "message": f"{TITLE} is running.", "version": VERSION, "description": DESCRIPTION}


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        async with db_manager.get_db() as conn:
            healthy = conn is not None
    except Exception:
        healthy = False

    return {
        "status": "healthy" if healthy else "degraded",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint."""
    favicon_path = os.path.join("app", "static", "favicon.ico")
    return FileResponse(favicon_path)
