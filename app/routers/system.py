"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from psycopg import sql
from psycopg.rows import dict_row

from ..auth import verify_admin
from ..config import global_settings
from ..exceptions import DatabaseUnavailableError
from ..tenant import Tenant
from ..utils import utils

router = APIRouter(tags=["System"])

schema_rate_limiter = utils.create_rate_limiter(
    max_requests=global_settings.rate_limit_default_max_requests,
    window_seconds=global_settings.rate_limit_default_window_seconds,
    scope="schemas_endpoint",
)


def _tenant(request: Request) -> Tenant:
    tenant: Tenant | None = getattr(request.state, "tenant", None)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not specified")
    return tenant


@router.get("/ready")
async def ready(request: Request):
    """Readiness probe for the resolved tenant."""
    tenant = _tenant(request)
    db_ready = await tenant.db_manager.is_db_available(timeout_seconds=2.0)
    if not db_ready:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "tenant": tenant.id, "checks": {"database": "down"}},
        )
    return {"status": "ready", "tenant": tenant.id, "checks": {"database": "up"}}


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


@router.get("/logs", dependencies=[Depends(verify_admin)])
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
    db_manager = _tenant(request).db_manager
    where_clauses: list[str] = []
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
            raise DatabaseUnavailableError()
        try:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(query, tuple(params))
                rows = await cursor.fetchall()
            await conn.commit()
        except Exception as exc:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"count": len(rows), "items": rows}


@router.get("/logs/db", dependencies=[Depends(verify_admin)])
async def get_db_logs(
    request: Request,
    request_id: str = Query(...),
    limit: int = Query(default=50, ge=1, le=500),
):
    """Return database-level logs linked to a specific API request."""
    db_manager = _tenant(request).db_manager
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
            raise DatabaseUnavailableError()
        try:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(query, (rid, limit))
                rows = await cursor.fetchall()
            await conn.commit()
        except Exception as exc:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"count": len(rows), "items": rows}


@router.get("/logs/ui", include_in_schema=False, dependencies=[Depends(verify_admin)])
async def logs_ui():
    """Serve the log viewer UI."""
    return FileResponse("app/static/logs.html", media_type="text/html")


@router.get("/schemas/{schema}", dependencies=[Depends(schema_rate_limiter)])
async def get_schema_endpoint(request: Request, schema: str):
    """Validate that a schema exists in the current tenant's database."""
    db_manager = _tenant(request).db_manager
    if not await db_manager.validate_schema(schema):
        raise HTTPException(status_code=404, detail=f"Schema '{schema}' not found")
    return {"status": "Accepted", "message": f"Schema '{schema}' is valid"}
