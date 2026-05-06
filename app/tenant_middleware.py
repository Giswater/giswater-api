"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from .config import global_settings
from .tenant import RESERVED_IDS, TENANT_ID_RE

# Path prefixes that should bypass tenant resolution. These are global routes
# that must work without a tenant context (health checks, static, admin API).
GLOBAL_PREFIXES = ("/health", "/static", "/favicon.ico", "/admin", "/docs", "/openapi.json", "/redoc")


def _extract_tenant(request: Request) -> str | None:
    host = (request.headers.get("host") or "").split(":")[0].lower()
    base = (global_settings.base_domain or "").lower()

    if base and host.endswith("." + base):
        candidate = host[: -(len(base) + 1)]
        return candidate or None

    if base and host == base:
        # apex never resolves a tenant in prod
        return None

    if global_settings.dev_allow_tenant_header:
        return request.headers.get("x-tenant-id")

    return None


def _is_valid_tenant_id(tid: str) -> bool:
    return bool(TENANT_ID_RE.match(tid)) and tid not in RESERVED_IDS


async def tenant_middleware(request: Request, call_next):
    path = request.url.path
    if path == "/" or any(path == p or path.startswith(p + "/") or path == p for p in GLOBAL_PREFIXES):
        return await call_next(request)

    tid = _extract_tenant(request)
    if not tid:
        return JSONResponse(status_code=404, content={"detail": "Tenant not specified"})
    if not _is_valid_tenant_id(tid):
        return JSONResponse(status_code=404, content={"detail": f"Invalid tenant id '{tid}'"})

    registry = getattr(request.app.state, "registry", None)
    if registry is None:
        return JSONResponse(status_code=503, content={"detail": "Tenant registry not initialized"})

    tenant = registry.get(tid)
    if tenant is None:
        return JSONResponse(status_code=404, content={"detail": f"Unknown tenant '{tid}'"})

    request.state.tenant = tenant
    return await call_next(request)
