"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

from fastapi import HTTPException

from app.auth.users import GwapiUserError
from app.core.exceptions import DatabaseUnavailableError, ProcedureError
from app.services.admin.tenant_service import TenantServiceError


def map_service_error(exc: Exception) -> HTTPException:  # noqa: C901
    """Map domain errors to HTTPException; re-raise errors with registered handlers."""
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, (ProcedureError, DatabaseUnavailableError)):
        raise exc
    if isinstance(exc, GwapiUserError):
        status = 404 if "not found" in str(exc).lower() else 400
        return HTTPException(status_code=status, detail=str(exc))
    if isinstance(exc, TenantServiceError):
        return HTTPException(status_code=exc.status_code, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    if isinstance(exc, LookupError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, KeyError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, RuntimeError):
        detail = str(exc)
        status = 502 if "Routing provider" in detail else 500
        return HTTPException(status_code=status, detail=detail)
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=500, detail=str(exc))
