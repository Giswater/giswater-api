"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, HTTPException, Request

from .. import gwapi_users
from ..gwapi_users import GwapiUserError
from ..models.gwapi_user_models import GwapiRoleOut, GwapiUserCreateIn, GwapiUserOut, GwapiUserUpdateIn
from ..tenant import TenantRegistry
from .admin import _audit_log, _registry, _require_writes

router = APIRouter(tags=["Admin - Users"])


def _require_basic_auth_tenant(tid: str, registry: TenantRegistry):
    tenant = registry.get(tid)
    if tenant is None:
        raise HTTPException(status_code=404, detail=f"Tenant '{tid}' not found")
    if tenant.settings.auth_mode != "basic":
        raise HTTPException(status_code=400, detail=f"Tenant '{tid}' is not configured for basic auth")
    if tenant.db_manager.connection_pool is None:
        raise HTTPException(status_code=503, detail=f"Tenant '{tid}' database unavailable")
    return tenant


def _to_out(record: gwapi_users.GwapiUserRecord) -> GwapiUserOut:
    return GwapiUserOut(
        username=record.username,
        db_role=record.db_role,
        enabled=record.enabled,
        roles=sorted(record.roles),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/tenants/{tid}/roles", response_model=list[GwapiRoleOut])
async def list_tenant_roles(tid: str, request: Request):
    registry = _registry()
    tenant = _require_basic_auth_tenant(tid, registry)
    roles = await gwapi_users.list_roles(tenant.db_manager)
    _audit_log(request, "list_roles", tid=tid)
    return [GwapiRoleOut(**role) for role in roles]


@router.get("/tenants/{tid}/users", response_model=list[GwapiUserOut])
async def list_tenant_users(tid: str, request: Request):
    registry = _registry()
    tenant = _require_basic_auth_tenant(tid, registry)
    users = await gwapi_users.list_users(tenant.db_manager)
    _audit_log(request, "list_users", tid=tid)
    return [_to_out(user) for user in users]


@router.post("/tenants/{tid}/users", response_model=GwapiUserOut, status_code=201)
async def create_tenant_user(tid: str, payload: GwapiUserCreateIn, request: Request):
    _require_writes()
    registry = _registry()
    tenant = _require_basic_auth_tenant(tid, registry)
    try:
        user = await gwapi_users.create_user(
            tenant.db_manager,
            username=payload.username,
            password=payload.password,
            db_role=payload.db_role,
            roles=payload.roles,
            enabled=payload.enabled,
        )
    except GwapiUserError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _audit_log(request, "create_user", tid=tid, username=payload.username)
    return _to_out(user)


@router.get("/tenants/{tid}/users/{username}", response_model=GwapiUserOut)
async def get_tenant_user(tid: str, username: str, request: Request):
    registry = _registry()
    tenant = _require_basic_auth_tenant(tid, registry)
    user = await gwapi_users.get_user(tenant.db_manager, username)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    _audit_log(request, "get_user", tid=tid, username=username)
    return _to_out(user)


@router.put("/tenants/{tid}/users/{username}", response_model=GwapiUserOut)
async def update_tenant_user(tid: str, username: str, payload: GwapiUserUpdateIn, request: Request):
    _require_writes()
    registry = _registry()
    tenant = _require_basic_auth_tenant(tid, registry)
    try:
        user = await gwapi_users.update_user(
            tenant.db_manager,
            username,
            password=payload.password,
            db_role=payload.db_role,
            roles=payload.roles,
            enabled=payload.enabled,
        )
    except GwapiUserError as exc:
        status = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    _audit_log(request, "update_user", tid=tid, username=username)
    return _to_out(user)


@router.delete("/tenants/{tid}/users/{username}", status_code=204)
async def delete_tenant_user(tid: str, username: str, request: Request):
    _require_writes()
    registry = _registry()
    tenant = _require_basic_auth_tenant(tid, registry)
    try:
        await gwapi_users.delete_user(tenant.db_manager, username)
    except GwapiUserError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit_log(request, "delete_user", tid=tid, username=username)
