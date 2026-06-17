"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations


class ProcedureError(Exception):
    """Raised when a database procedure returns non-Accepted status."""

    def __init__(self, result: dict):
        self.result = result


class DatabaseUnavailableError(Exception):
    """Raised when the database cannot be reached."""


class InvalidParametersError(ValueError):
    """Invalid request parameters parsed in the service layer (HTTP 422)."""


def db_unavailable_payload() -> dict:
    return {
        "status": "Failed",
        "message": {"level": 2, "text": "Database unavailable. Please retry later."},
        "error": "database_unavailable",
    }
