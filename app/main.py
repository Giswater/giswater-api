"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import DatabaseManager
from .keycloak import idp, config
from .utils import utils
from .exceptions import ProcedureError, procedure_error_handler
from .routers.basic import basic
from .routers.om import mincut
from .routers.waterbalance import water_balance
from .routers.epa import hydraulic_engine_ud, hydraulic_engine_ws
from .routers.routing import routing
from .routers.crm import crm
from .models.util_models import GwErrorResponse

TITLE = "Giswater API"
VERSION = "0.5.0"
DESCRIPTION = "API for interacting with a Giswater database."

# Database manager
db_manager = DatabaseManager(config)

# Create FastAPI app
app = FastAPI(
    version=VERSION,
    title=TITLE,
    description=DESCRIPTION,
    root_path="/api/v1",
    responses={
        500: {
            "model": GwErrorResponse,
            "description": "Database function error"
        }
    }
)

# Register exception handlers
app.add_exception_handler(ProcedureError, procedure_error_handler)

# Add Keycloak Swagger config if enabled
if idp:
    idp.add_swagger_config(app)

# Store in app.state for access in routes
app.state.config = config
app.state.db_manager = db_manager

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers conditionally based on config
if config.get_bool("api", "basic"):
    app.include_router(basic.router)
if config.get_bool("api", "mincut"):
    app.include_router(mincut.router)
if config.get_bool("api", "water_balance"):
    app.include_router(water_balance.router)
if config.get_bool("api", "routing"):
    app.include_router(routing.router)
if config.get_bool("api", "crm"):
    app.include_router(crm.router)
if config.get_bool("hydraulic_engine", "enabled"):
    if config.get_bool("hydraulic_engine", "ud"):
        app.include_router(hydraulic_engine_ud.router)
    if config.get_bool("hydraulic_engine", "ws"):
        app.include_router(hydraulic_engine_ws.router)

# Load plugins
utils.load_plugins(app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "Accepted",
        "message": f"{TITLE} is running.",
        "version": VERSION,
        "description": DESCRIPTION
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        with db_manager.get_db() as conn:
            healthy = conn is not None
    except Exception:
        healthy = False

    return {
        "status": "healthy" if healthy else "degraded",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint."""
    favicon_path = os.path.join("app", "static", "favicon.ico")
    return FileResponse(favicon_path)
