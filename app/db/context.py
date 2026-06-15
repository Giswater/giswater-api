"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import contextvars
import uuid
from dataclasses import dataclass

REQUEST_ID_CTX: contextvars.ContextVar[uuid.UUID | None] = contextvars.ContextVar("request_id", default=None)


@dataclass(frozen=True)
class DbIdentity:
    """Request-scoped DB user for SET ROLE (set by common_parameters)."""

    username: str | None
    db_role: str | None


DB_IDENTITY_CTX: contextvars.ContextVar[DbIdentity | None] = contextvars.ContextVar("db_identity", default=None)


def _db_identity(user: str | None, db_role: str | None = None) -> str | None:
    if user == "anonymous" or user is None:
        return None
    return db_role if db_role is not None else user


def _resolve_db_identity(user: str | None = "anonymous", db_role: str | None = None) -> str | None:
    """Merge explicit args with DB_IDENTITY_CTX; used by execute_* for SET ROLE."""
    ctx = DB_IDENTITY_CTX.get()
    if ctx is not None:
        if user is None or user == "anonymous":
            user = ctx.username if ctx.username is not None else "anonymous"
            if db_role is None:
                db_role = ctx.db_role
        elif db_role is None and user == ctx.username:
            db_role = ctx.db_role
    return _db_identity(user, db_role)
