"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from . import state
from .config import global_settings
from .constants import ADMIN_PREFIX, GLOBAL_HEALTH_PATH, STATIC_PREFIX, TENANT_PREFIX
from .tenant import RESERVED_IDS, TENANT_ID_RE


def _extract_tenant_id(request: Request) -> str | None:
    if global_settings.dev_allow_tenant_header and request.headers.get("x-tenant-id"):
        return request.headers.get("x-tenant-id", "").strip() or None

    host = (request.headers.get("host") or "").split(":")[0].lower()
    base = (global_settings.base_domain or "").lower()

    if base and host.endswith("." + base):
        candidate = host[: -(len(base) + 1)]
        return candidate or None

    if base and host == base:
        return None

    if global_settings.dev_allow_tenant_header:
        return request.headers.get("x-tenant-id")

    return None


def _is_valid_tenant_id(tid: str) -> bool:
    return bool(TENANT_ID_RE.match(tid)) and tid not in RESERVED_IDS


def _is_apex_host(request: Request) -> bool:
    host = (request.headers.get("host") or "").split(":")[0].lower()
    base = (global_settings.base_domain or "").lower()
    return bool(base) and host == base


def _path_starts(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


async def host_middleware(request: Request, call_next):  # noqa: C901
    path = request.url.path

    # Liveness: no tenant context
    if path == GLOBAL_HEALTH_PATH or path.startswith(GLOBAL_HEALTH_PATH + "/"):
        return await call_next(request)

    if _path_starts(path, STATIC_PREFIX):
        return await call_next(request)

    apex = _is_apex_host(request)

    if _path_starts(path, ADMIN_PREFIX):
        if not apex:
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        return await call_next(request)

    if _path_starts(path, TENANT_PREFIX):
        if apex:
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        tid = _extract_tenant_id(request)
        if not tid:
            return JSONResponse(status_code=404, content={"detail": "Tenant not specified"})
        if not _is_valid_tenant_id(tid):
            return JSONResponse(status_code=404, content={"detail": f"Invalid tenant id '{tid}'"})

        reg = state.registry
        if reg is None:
            return JSONResponse(status_code=503, content={"detail": "Tenant registry not initialized"})

        tenant = reg.get(tid)
        if tenant is None:
            return JSONResponse(status_code=404, content={"detail": f"Unknown tenant '{tid}'"})

        request.state.tenant = tenant
        return await call_next(request)

    return JSONResponse(status_code=404, content={"detail": "Not found"})
