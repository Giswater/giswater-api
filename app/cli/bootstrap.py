"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, TypeVar

from app.core.config import global_settings
from app.core.exceptions import ProcedureError
from app.services.context import ServiceContext, service_context_from_tenant
from app.tenancy.registry import Tenant, TenantRegistry

_registry: TenantRegistry | None = None
T = TypeVar("T")


async def get_registry(tenants_dir: str | None = None) -> TenantRegistry:
    global _registry
    if _registry is not None:
        return _registry
    path = Path(tenants_dir or global_settings.tenants_dir).resolve()
    registry = TenantRegistry(path)
    await registry.load_all()
    _registry = registry
    return registry


async def close_registry() -> None:
    global _registry
    if _registry is not None:
        await _registry.close_all()
        _registry = None


def run_async(coro: Awaitable[T]) -> T:
    return asyncio.run(coro)


async def resolve_tenant(tenant_id: str, tenants_dir: str | None = None) -> Tenant:
    registry = await get_registry(tenants_dir)
    tenant = registry.get(tenant_id)
    if tenant is None:
        raise LookupError(f"Tenant '{tenant_id}' not found")
    return tenant


def build_tenant_context(
    tenant: Tenant,
    *,
    schema: str,
    user: str | None = None,
    db_role: str | None = None,
    device: int = 5,
    lang: str = "es_ES",
) -> ServiceContext:
    return service_context_from_tenant(
        tenant,
        schema=schema,
        user_id=user,
        db_role=db_role or user,
        device=device,
        lang=lang,
    )


def emit_json(data: object, *, exit_code: int = 0) -> None:
    print(json.dumps(data, default=str, indent=2))
    raise SystemExit(exit_code)


def run_service(coro_factory: Callable[[], Awaitable[Any]]) -> Any:
    """Run an async service call; map domain errors to JSON + exit code."""

    async def _wrapped() -> Any:
        try:
            return await coro_factory()
        finally:
            await close_registry()

    try:
        return run_async(_wrapped())
    except ProcedureError as exc:
        emit_json(exc.result, exit_code=1)
    except Exception as exc:
        emit_json({"status": "Failed", "message": str(exc)}, exit_code=1)


def tenants_dir_from_ctx(ctx_obj: dict) -> str | None:
    return ctx_obj.get("tenants_dir")
