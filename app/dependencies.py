"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import secrets
from typing import Annotated, Literal
from fastapi import Depends, Query, Header, Request, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_keycloak import OIDCUser
from .config import settings
from .keycloak import idp, get_current_user


async def get_schema(
    request: Request,
    schema: str = Query(..., description="Database schema name", examples=["public"]),
):
    """
    Dependency to get and validate schema parameter.

    Args:
        schema: Schema name from query parameter
        request: Request object to access db_manager from app.state

    Returns:
        Schema name if valid

    Raises:
        HTTPException: If schema is not found
    """
    if hasattr(request.app.state, "db_manager"):
        db_manager = request.app.state.db_manager
        if not await db_manager.validate_schema(schema):
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{schema}' not found",
            )
    # If no db_manager available (shouldn't happen in normal operation), just return schema
    return schema


async def common_parameters(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),  # noqa: B008
    schema: str = Depends(get_schema),
    device: int = Header(
        default=5,
        alias="X-Device",
        description=(
            "Device identifier. Valid values: 1 = Mobile, 2 = Tablet, 3 = Web Desktop, 4 = QGIS Desktop, 5 = QGIS Web"
        ),
        ge=1,
        le=5,
    ),
    lang: Literal["es_ES", "es_CR", "en_US", "pt_BR", "pt_PT", "fr_FR", "ca_ES"] = Header(
        default="es_ES",
        alias="X-Lang",
        description="Language code",
        examples=["es_ES", "es_CR", "en_US", "pt_BR", "pt_PT", "fr_FR", "ca_ES"],
    ),
):
    db_manager = request.app.state.db_manager
    if not await db_manager.validate_schema(schema):
        raise HTTPException(status_code=404, detail=f"Schema '{schema}' not found")
    return {
        "request": request,
        "user_id": current_user.preferred_username,
        "schema": schema,
        "device": device,
        "lang": lang,
        "db_manager": db_manager,
        "api_version": request.app.version,
    }


CommonsDep = Annotated[dict, Depends(common_parameters)]


def verify_log_admin():
    """
    Returns the appropriate auth dependency for the /logs endpoint.
    Keycloak on  → requires 'log-admin' role.
    Keycloak off → falls back to HTTP Basic with env credentials.
    """
    if idp:
        return idp.get_current_user(required_roles=["log-admin"])

    _security = HTTPBasic()

    async def _check_basic(request: Request, credentials: HTTPBasicCredentials = Depends(_security)):
        if not settings.log_admin_password:
            raise HTTPException(status_code=403, detail="Log admin access not configured")
        correct_user = secrets.compare_digest(credentials.username, settings.log_admin_user)
        correct_pass = secrets.compare_digest(credentials.password, settings.log_admin_password)
        if not correct_user or not correct_pass:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        request.state.user = credentials.username

    return _check_basic
