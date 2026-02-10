"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import os
import uuid
from datetime import date, datetime
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from psycopg import sql
from psycopg.rows import dict_row

from .database import DatabaseManager
from .keycloak import idp
from .config import settings
from .utils import utils
from .dependencies import verify_log_admin
from .exceptions import ProcedureError, procedure_error_handler
from .logging import request_logging_middleware
from .routers.basic import basic
from .routers.om import mincut, profile, flow, waterbalance
from .routers.om.mapzones import dma, sector, presszone, dqa, omzone, omunit
from .routers.routing import routing
from .routers.crm import crm
from .models.util_models import GwErrorResponse

TITLE = "Giswater API"
VERSION = "0.7.0"
DESCRIPTION = "API for interacting with a Giswater database."

# Database manager
db_manager = DatabaseManager()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db_manager.init_conn_pool()
    if settings.log_db_enabled:
        try:
            await utils.ensure_log_schema(db_manager)
        except Exception as exc:
            print(f"Failed to initialize log schema: {exc}")
    app_logger = utils.create_log("api")
    api_log_date = date.today().strftime("%Y%m%d")
    try:
        app.state.api_logger = app_logger
        app.state.api_log_date = api_log_date
        yield
    finally:
        await db_manager.close()


# Create FastAPI app
app = FastAPI(
    version=VERSION,
    title=TITLE,
    description=DESCRIPTION,
    root_path="/api/v1",
    responses={500: {"model": GwErrorResponse, "description": "Database function error"}},
    lifespan=lifespan,
)

# Request logging middleware
app.middleware("http")(request_logging_middleware)

# Register exception handlers
app.add_exception_handler(ProcedureError, procedure_error_handler)  # type: ignore

# Add Keycloak Swagger config if enabled
if idp:
    idp.add_swagger_config(app)

# Store in app.state for access in routes
app.state.settings = settings
app.state.db_manager = db_manager


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
    app.include_router(waterbalance.router)
if settings.api_mapzones:
    app.include_router(dma.router)
    app.include_router(sector.router)
    app.include_router(presszone.router)
    app.include_router(dqa.router)
    app.include_router(omzone.router)
    app.include_router(omunit.router)
if settings.api_routing:
    app.include_router(routing.router)
if settings.api_crm:
    app.include_router(crm.router)
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


def _manage_where_clauses(where_clauses: list, params: list, from_, to, endpoint, method, status, user):
    if from_:
        where_clauses.append("ts >= %s")
        params.append(from_)
    if to:
        where_clauses.append("ts <= %s")
        params.append(to)
    if endpoint:
        where_clauses.append("endpoint = %s")
        params.append(endpoint)
    if method:
        where_clauses.append("method = %s")
        params.append(method.upper())
    if status is not None:
        where_clauses.append("status = %s")
        params.append(status)
    if user:
        where_clauses.append("user_name = %s")
        params.append(user)


@app.get("/logs", dependencies=[Depends(verify_log_admin())])
async def get_logs(
    request: Request,
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = Query(default=None, alias="to"),
    endpoint: str | None = Query(default=None),
    method: str | None = Query(default=None),
    status: int | None = Query(default=None),
    user: str | None = Query(default=None),
    request_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    db_manager = request.app.state.db_manager
    where_clauses = []
    params: list = []
    _manage_where_clauses(where_clauses, params, from_, to, endpoint, method, status, user)
    if request_id:
        try:
            params.append(uuid.UUID(request_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid request_id") from exc
        where_clauses.append("request_id = %s")

    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)

    query = sql.SQL(
        f"""
        SELECT ts, endpoint, method, status, duration_ms, user_name, request_id,
               client_ip, query_params, body_size, response_size,
               request_headers, request_body, response_headers, response_body,
               EXISTS (
                   SELECT 1 FROM {{schema}}.{{db_table}} d
                   WHERE d.request_id = main.request_id
               ) AS has_db_logs
        FROM {{schema}}.{{table}} main
        {where_sql}
        ORDER BY ts DESC
        LIMIT %s OFFSET %s
        """
    ).format(
        schema=sql.Identifier(utils.LOG_SCHEMA),
        table=sql.Identifier(utils.LOG_TABLE),
        db_table=sql.Identifier(utils.LOG_DB_TABLE),
    )
    params.extend([limit, offset])

    async with db_manager.get_db() as conn:
        if conn is None:
            raise HTTPException(status_code=500, detail="No connection to database")
        try:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(query, tuple(params))
                rows = await cursor.fetchall()
            await conn.commit()
        except Exception as exc:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"count": len(rows), "items": rows}


@app.get("/logs/db", dependencies=[Depends(verify_log_admin())])
async def get_db_logs(
    request: Request,
    request_id: str = Query(...),
    limit: int = Query(default=50, ge=1, le=500),
):
    """Return database-level logs linked to a specific API request."""
    db_manager = request.app.state.db_manager
    try:
        rid = uuid.UUID(request_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid request_id") from exc

    query = sql.SQL(
        """
        SELECT ts, request_id, schema_name, function_name, sql_text,
               response_json, duration_ms, status, error
        FROM {schema}.{table}
        WHERE request_id = %s
        ORDER BY ts ASC
        LIMIT %s
        """
    ).format(schema=sql.Identifier(utils.LOG_SCHEMA), table=sql.Identifier(utils.LOG_DB_TABLE))

    async with db_manager.get_db() as conn:
        if conn is None:
            raise HTTPException(status_code=500, detail="No connection to database")
        try:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(query, (rid, limit))
                rows = await cursor.fetchall()
            await conn.commit()
        except Exception as exc:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"count": len(rows), "items": rows}


@app.get("/logs/ui", include_in_schema=False, dependencies=[Depends(verify_log_admin())])
async def logs_ui():
    """Serve the log viewer UI."""
    return FileResponse("app/static/logs.html", media_type="text/html")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint."""
    favicon_path = os.path.join("app", "static", "favicon.ico")
    return FileResponse(favicon_path)
