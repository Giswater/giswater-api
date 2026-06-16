"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from app.core.config import global_settings
from app.schemas.admin import TenantCreateIn, TenantIn, TenantOut
from app.tenancy import state
from app.tenancy.registry import TenantRegistry
from app.api.http_errors import map_service_error
from app.services.admin.tenant_service import TenantService

router = APIRouter(tags=["Admin"])

_audit = logging.getLogger("admin.audit")


def _registry() -> TenantRegistry:
    reg = state.registry
    if reg is None:
        raise HTTPException(status_code=503, detail="Tenant registry not initialized")
    return reg


def _require_writes() -> None:
    if not global_settings.admin_write_enabled:
        raise HTTPException(status_code=403, detail="Tenant writes disabled")


def _audit_log(request: Request, action: str, tid: str | None = None, **extra) -> None:
    actor = getattr(request.state, "user", None)
    _audit.info(
        "admin %s actor=%s tenant=%s extras=%s",
        action,
        actor,
        tid,
        extra,
    )


@router.get("/tenants", response_model=list[TenantOut])
async def list_tenants():
    return TenantService(_registry()).list_tenants()


@router.get("/tenants/{tid}", response_model=TenantOut)
async def get_tenant(tid: str):
    try:
        return TenantService(_registry()).get_tenant(tid)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.post("/tenants", response_model=TenantOut, status_code=201)
async def create_tenant(payload: TenantCreateIn, request: Request):
    try:
        tenant = await TenantService(_registry()).create_tenant(payload)
        _audit_log(request, "create", tid=payload.id)
        return tenant
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.put("/tenants/{tid}", response_model=TenantOut)
async def update_tenant(tid: str, payload: TenantIn, request: Request):
    try:
        tenant = await TenantService(_registry()).update_tenant(tid, payload)
        _audit_log(request, "update", tid=tid)
        return tenant
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.delete("/tenants/{tid}", status_code=204)
async def delete_tenant(tid: str, request: Request):
    try:
        await TenantService(_registry()).delete_tenant(tid)
        _audit_log(request, "delete", tid=tid)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.post("/tenants/{tid}/reload", response_model=TenantOut)
async def reload_tenant(tid: str, request: Request):
    try:
        tenant = await TenantService(_registry()).reload_tenant(tid)
        _audit_log(request, "reload_one", tid=tid)
        return tenant
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.post("/tenants/reload")
async def reload_tenants(request: Request):
    try:
        result = await TenantService(_registry()).reload_all()
        _audit_log(request, "reload_all", **result)
        return result
    except Exception as exc:
        raise map_service_error(exc) from exc
