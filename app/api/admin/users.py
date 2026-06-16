"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging

from fastapi import APIRouter, Request

from app.auth.schemas import GwapiRoleOut, GwapiUserCreateIn, GwapiUserOut, GwapiUserUpdateIn
from app.api.admin.tenants import _audit_log, _registry
from app.api.http_errors import map_service_error
from app.services.admin.user_service import GwapiUserService

router = APIRouter(tags=["Admin - Users"])
_audit = logging.getLogger("admin.audit")


@router.get("/tenants/{tid}/roles", response_model=list[GwapiRoleOut])
async def list_tenant_roles(tid: str, request: Request):
    try:
        roles = await GwapiUserService(_registry()).list_roles(tid)
        _audit_log(request, "list_roles", tid=tid)
        return roles
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get("/tenants/{tid}/users", response_model=list[GwapiUserOut])
async def list_tenant_users(tid: str, request: Request):
    try:
        users = await GwapiUserService(_registry()).list_users(tid)
        _audit_log(request, "list_users", tid=tid)
        return users
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.post("/tenants/{tid}/users", response_model=GwapiUserOut, status_code=201)
async def create_tenant_user(tid: str, payload: GwapiUserCreateIn, request: Request):
    try:
        user = await GwapiUserService(_registry()).create_user(
            tid,
            username=payload.username,
            password=payload.password,
            db_role=payload.db_role,
            roles=payload.roles,
            enabled=payload.enabled,
        )
        _audit_log(request, "create_user", tid=tid, username=payload.username)
        return user
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get("/tenants/{tid}/users/{username}", response_model=GwapiUserOut)
async def get_tenant_user(tid: str, username: str, request: Request):
    try:
        user = await GwapiUserService(_registry()).get_user(tid, username)
        _audit_log(request, "get_user", tid=tid, username=username)
        return user
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.put("/tenants/{tid}/users/{username}", response_model=GwapiUserOut)
async def update_tenant_user(tid: str, username: str, payload: GwapiUserUpdateIn, request: Request):
    try:
        user = await GwapiUserService(_registry()).update_user(
            tid,
            username,
            password=payload.password,
            db_role=payload.db_role,
            roles=payload.roles,
            enabled=payload.enabled,
        )
        _audit_log(request, "update_user", tid=tid, username=username)
        return user
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.delete("/tenants/{tid}/users/{username}", status_code=204)
async def delete_tenant_user(tid: str, username: str, request: Request):
    try:
        await GwapiUserService(_registry()).delete_user(tid, username)
        _audit_log(request, "delete_user", tid=tid, username=username)
    except Exception as exc:
        raise map_service_error(exc) from exc
