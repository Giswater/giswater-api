"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from ..auth import verify_admin
from ..config import global_settings
from ..schemas.admin import (
    TenantCreateIn,
    TenantIn,
    TenantOut,
    build_tenant_settings_from_input,
)
from ..tenant import RESERVED_IDS, TENANT_ID_RE, TenantRegistry, validate_tenant_id

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(verify_admin)])

_audit = logging.getLogger("admin.audit")


def _registry(request: Request) -> TenantRegistry:
    registry = getattr(request.app.state, "registry", None)
    if registry is None:
        raise HTTPException(status_code=503, detail="Tenant registry not initialized")
    return registry


def _require_writes() -> None:
    if not global_settings.admin_write_enabled:
        raise HTTPException(status_code=403, detail="Tenant writes disabled")


def _validate_id_or_409(tid: str, registry: TenantRegistry) -> None:
    if not TENANT_ID_RE.match(tid) or tid in RESERVED_IDS:
        raise HTTPException(status_code=400, detail=f"Invalid tenant id '{tid}'")
    if registry.get(tid) is not None:
        raise HTTPException(status_code=409, detail=f"Tenant '{tid}' already exists")


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
async def list_tenants(request: Request):
    registry = _registry(request)
    return [TenantOut.from_tenant(t) for t in registry.all()]


@router.get("/tenants/{tid}", response_model=TenantOut)
async def get_tenant(tid: str, request: Request):
    registry = _registry(request)
    tenant = registry.get(tid)
    if tenant is None:
        raise HTTPException(status_code=404, detail=f"Tenant '{tid}' not found")
    return TenantOut.from_tenant(tenant)


@router.post("/tenants", response_model=TenantOut, status_code=201)
async def create_tenant(payload: TenantCreateIn, request: Request):
    _require_writes()
    registry = _registry(request)
    _validate_id_or_409(payload.id, registry)
    settings = build_tenant_settings_from_input(payload)
    try:
        tenant = await registry.create(payload.id, settings)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _audit_log(request, "create", tid=payload.id)
    return TenantOut.from_tenant(tenant)


@router.put("/tenants/{tid}", response_model=TenantOut)
async def update_tenant(tid: str, payload: TenantIn, request: Request):
    _require_writes()
    registry = _registry(request)
    existing = registry.get(tid)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Tenant '{tid}' not found")
    settings = build_tenant_settings_from_input(payload, existing=existing.settings)
    try:
        tenant = await registry.update(tid, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit_log(request, "update", tid=tid)
    return TenantOut.from_tenant(tenant)


@router.delete("/tenants/{tid}", status_code=204)
async def delete_tenant(tid: str, request: Request):
    _require_writes()
    registry = _registry(request)
    try:
        await registry.delete(tid)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit_log(request, "delete", tid=tid)


@router.post("/tenants/{tid}/reload", response_model=TenantOut)
async def reload_tenant(tid: str, request: Request):
    _require_writes()
    registry = _registry(request)
    try:
        validate_tenant_id(tid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        tenant = await registry.reload_one(tid)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit_log(request, "reload_one", tid=tid)
    return TenantOut.from_tenant(tenant)


@router.post("/tenants/reload")
async def reload_tenants(request: Request):
    if not global_settings.admin_reload_enabled:
        raise HTTPException(status_code=403, detail="Reload disabled")
    registry = _registry(request)
    result = await registry.reload()
    _audit_log(request, "reload_all", **result)
    return result
