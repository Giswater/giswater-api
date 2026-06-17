"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.users import GwapiUserError
from app.core.exceptions import (
    DatabaseUnavailableError,
    InvalidParametersError,
    ProcedureError,
    db_unavailable_payload,
)
from app.services.admin.tenant_service import TenantServiceError

logger = logging.getLogger(__name__)


async def procedure_error_handler(_request: Request, exc: ProcedureError) -> JSONResponse:
    """Giswater procedure failure — body matches DB shape (status/message/version/body)."""
    logger.warning("ProcedureError on %s", _request.url.path)
    return JSONResponse(status_code=500, content=exc.result)


async def database_unavailable_error_handler(_request: Request, exc: DatabaseUnavailableError) -> JSONResponse:
    logger.error("DatabaseUnavailableError on %s", _request.url.path)
    return JSONResponse(status_code=503, content=db_unavailable_payload())


async def invalid_parameters_handler(_request: Request, exc: InvalidParametersError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def lookup_error_handler(_request: Request, exc: LookupError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def gwapi_user_error_handler(_request: Request, exc: GwapiUserError) -> JSONResponse:
    status = 404 if "not found" in str(exc).lower() else 400
    return JSONResponse(status_code=status, content={"detail": str(exc)})


async def tenant_service_error_handler(_request: Request, exc: TenantServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


async def runtime_error_handler(_request: Request, exc: RuntimeError) -> JSONResponse:
    detail = str(exc)
    status = 502 if "Routing provider" in detail else 500
    return JSONResponse(status_code=status, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    """Wire service-layer exceptions to HTTP responses (call once per FastAPI sub-app)."""
    app.add_exception_handler(ProcedureError, procedure_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(DatabaseUnavailableError, database_unavailable_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidParametersError, invalid_parameters_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValueError, value_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(LookupError, lookup_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(GwapiUserError, gwapi_user_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(TenantServiceError, tenant_service_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RuntimeError, runtime_error_handler)  # type: ignore[arg-type]
