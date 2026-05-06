"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from typing import Annotated, Literal

from fastapi import Depends, Header, HTTPException, Query, Request
from fastapi_keycloak import OIDCUser

from .auth import get_current_user_dep, verify_admin
from .tenant import Tenant


def _get_tenant(request: Request) -> Tenant:
    tenant: Tenant | None = getattr(request.state, "tenant", None)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not specified")
    return tenant


async def get_schema(
    request: Request,
    schema: str = Query(..., description="Database schema name", examples=["public"]),
):
    """Validate that `schema` exists in the current tenant's database."""
    tenant = _get_tenant(request)
    if not await tenant.db_manager.validate_schema(schema):
        raise HTTPException(status_code=404, detail=f"Schema '{schema}' not found")
    return schema


async def common_parameters(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user_dep()),  # noqa: B008
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
    tenant = _get_tenant(request)
    return {
        "request": request,
        "user_id": current_user.preferred_username,
        "schema": schema,
        "device": device,
        "lang": lang,
        "db_manager": tenant.db_manager,
        "tenant": tenant,
        "api_version": request.app.version,
    }


CommonsDep = Annotated[dict, Depends(common_parameters)]


def require_feature(flag: str):
    """Router-level dep that 404s when the tenant has the API toggle off."""

    async def _check(request: Request) -> None:
        tenant = _get_tenant(request)
        if not getattr(tenant.settings, flag, False):
            raise HTTPException(status_code=404, detail="Feature disabled")

    return _check


def verify_log_admin():
    """Backward-compat wrapper around `verify_admin` for legacy /logs endpoints."""
    return verify_admin
