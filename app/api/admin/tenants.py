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
from app.services.admin.tenant_service import TenantService
from app.tenancy import state
from app.tenancy.registry import TenantRegistry

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


@router.get("/tenants", description="List all configured tenants.", response_model=list[TenantOut])
async def list_tenants():
    return TenantService(_registry()).list_tenants()


@router.get("/tenants/{tid}", description="Get a tenant by id.", response_model=TenantOut)
async def get_tenant(tid: str):
    return TenantService(_registry()).get_tenant(tid)


@router.post("/tenants", description="Create a new tenant.", response_model=TenantOut, status_code=201)
async def create_tenant(payload: TenantCreateIn, request: Request):
    tenant = await TenantService(_registry()).create_tenant(payload)
    _audit_log(request, "create", tid=payload.id)
    return tenant


@router.put("/tenants/{tid}", description="Update a tenant configuration.", response_model=TenantOut)
async def update_tenant(tid: str, payload: TenantIn, request: Request):
    tenant = await TenantService(_registry()).update_tenant(tid, payload)
    _audit_log(request, "update", tid=tid)
    return tenant


@router.delete("/tenants/{tid}", description="Delete a tenant.", status_code=204)
async def delete_tenant(tid: str, request: Request):
    await TenantService(_registry()).delete_tenant(tid)
    _audit_log(request, "delete", tid=tid)


@router.post("/tenants/{tid}/reload", description="Reload a single tenant from disk.", response_model=TenantOut)
async def reload_tenant(tid: str, request: Request):
    tenant = await TenantService(_registry()).reload_tenant(tid)
    _audit_log(request, "reload_one", tid=tid)
    return tenant


@router.post("/tenants/reload", description="Reload all tenants from disk.")
async def reload_tenants(request: Request):
    result = await TenantService(_registry()).reload_all()
    _audit_log(request, "reload_all", **result)
    return result
