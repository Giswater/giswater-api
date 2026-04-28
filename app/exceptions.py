"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class ProcedureError(Exception):
    """Raised when a database procedure returns non-Accepted status"""

    def __init__(self, result: dict):
        self.result = result


class DatabaseUnavailableError(Exception):
    """Raised when the database cannot be reached."""


def db_unavailable_payload() -> dict:
    return {
        "status": "Failed",
        "message": {"level": 2, "text": "Database unavailable. Please retry later."},
        "error": "database_unavailable",
    }


async def procedure_error_handler(request: Request, exc: ProcedureError):
    # Add your logging here - you have access to request.url, request.headers, etc.
    return JSONResponse(status_code=500, content=exc.result)


async def database_unavailable_error_handler(request: Request, exc: DatabaseUnavailableError):
    # Add your logging here - you have access to request.url, request.headers, etc.
    return JSONResponse(status_code=503, content=db_unavailable_payload())
