"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Request

from app.api.admin.tenants import _audit_log, _registry
from app.auth.schemas import GwapiRoleOut, GwapiUserCreateIn, GwapiUserOut, GwapiUserUpdateIn
from app.services.admin.user_service import GwapiUserService

router = APIRouter(tags=["Admin - Users"])


@router.get("/tenants/{tid}/roles", description="List gwapi roles for a tenant.", response_model=list[GwapiRoleOut])
async def list_tenant_roles(tid: str, request: Request):
    roles = await GwapiUserService(_registry()).list_roles(tid)
    _audit_log(request, "list_roles", tid=tid)
    return roles


@router.get("/tenants/{tid}/users", description="List gwapi users for a tenant.", response_model=list[GwapiUserOut])
async def list_tenant_users(tid: str, request: Request):
    users = await GwapiUserService(_registry()).list_users(tid)
    _audit_log(request, "list_users", tid=tid)
    return users


@router.post(
    "/tenants/{tid}/users",
    description="Create a gwapi user for a tenant.",
    response_model=GwapiUserOut,
    status_code=201,
)
async def create_tenant_user(tid: str, payload: GwapiUserCreateIn, request: Request):
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


@router.get(
    "/tenants/{tid}/users/{username}",
    description="Get a gwapi user by username.",
    response_model=GwapiUserOut,
)
async def get_tenant_user(tid: str, username: str, request: Request):
    user = await GwapiUserService(_registry()).get_user(tid, username)
    _audit_log(request, "get_user", tid=tid, username=username)
    return user


@router.put(
    "/tenants/{tid}/users/{username}",
    description="Update a gwapi user.",
    response_model=GwapiUserOut,
)
async def update_tenant_user(tid: str, username: str, payload: GwapiUserUpdateIn, request: Request):
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


@router.delete(
    "/tenants/{tid}/users/{username}",
    description="Delete a gwapi user.",
    status_code=204,
)
async def delete_tenant_user(tid: str, username: str, request: Request):
    await GwapiUserService(_registry()).delete_user(tid, username)
    _audit_log(request, "delete_user", tid=tid, username=username)
