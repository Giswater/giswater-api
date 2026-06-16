"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

from app.auth import users as gwapi_users
from app.auth.schemas import GwapiRoleOut, GwapiUserOut
from app.auth.users import GwapiUserError, GwapiUserRecord
from app.services.admin.tenant_service import TenantService, TenantServiceError
from app.tenancy.registry import TenantRegistry


class GwapiUserService:
    def __init__(self, registry: TenantRegistry):
        self._tenants = TenantService(registry)

    def _require_basic_auth_tenant(self, tid: str):
        tenant = self._tenants.get_tenant_record(tid)
        if tenant.settings.auth_mode != "basic":
            raise TenantServiceError(f"Tenant '{tid}' is not configured for basic auth", status_code=400)
        if tenant.db_manager.connection_pool is None:
            raise TenantServiceError(f"Tenant '{tid}' database unavailable", status_code=503)
        return tenant

    @staticmethod
    def _to_out(record: GwapiUserRecord) -> GwapiUserOut:
        return GwapiUserOut(
            username=record.username,
            db_role=record.db_role,
            enabled=record.enabled,
            roles=sorted(record.roles),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    async def list_roles(self, tid: str) -> list[GwapiRoleOut]:
        tenant = self._require_basic_auth_tenant(tid)
        roles = await gwapi_users.list_roles(tenant.db_manager)
        return [GwapiRoleOut(**role) for role in roles]

    async def list_users(self, tid: str) -> list[GwapiUserOut]:
        tenant = self._require_basic_auth_tenant(tid)
        users = await gwapi_users.list_users(tenant.db_manager)
        return [self._to_out(user) for user in users]

    async def create_user(
        self,
        tid: str,
        *,
        username: str,
        password: str,
        db_role: str | None,
        roles: list[str],
        enabled: bool,
    ) -> GwapiUserOut:
        self._tenants.require_writes()
        tenant = self._require_basic_auth_tenant(tid)
        user = await gwapi_users.create_user(
            tenant.db_manager,
            username=username,
            password=password,
            db_role=db_role,
            roles=roles,
            enabled=enabled,
        )
        return self._to_out(user)

    async def get_user(self, tid: str, username: str) -> GwapiUserOut:
        tenant = self._require_basic_auth_tenant(tid)
        user = await gwapi_users.get_user(tenant.db_manager, username)
        if user is None:
            raise GwapiUserError(f"User '{username}' not found")
        return self._to_out(user)

    async def update_user(
        self,
        tid: str,
        username: str,
        *,
        password: str | None,
        db_role: str | None,
        roles: list[str] | None,
        enabled: bool | None,
    ) -> GwapiUserOut:
        self._tenants.require_writes()
        tenant = self._require_basic_auth_tenant(tid)
        user = await gwapi_users.update_user(
            tenant.db_manager,
            username,
            password=password,
            db_role=db_role,
            roles=roles,
            enabled=enabled,
        )
        return self._to_out(user)

    async def delete_user(self, tid: str, username: str) -> None:
        self._tenants.require_writes()
        tenant = self._require_basic_auth_tenant(tid)
        await gwapi_users.delete_user(tenant.db_manager, username)
