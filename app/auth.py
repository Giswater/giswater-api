"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import asyncio
import secrets
import time
from typing import Optional

import httpx
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_keycloak import FastAPIKeycloak, OIDCUser

from .config import global_settings

_basic = HTTPBasic(auto_error=False)

# JWKS cache for the platform realm (separate from tenant idps which cache their own).
_PLATFORM_JWKS_TTL = 3600.0
_platform_jwks_cache: dict[str, tuple[float, dict]] = {}
_platform_jwks_lock = asyncio.Lock()


def verify_token(token: str, idp: FastAPIKeycloak) -> OIDCUser:
    """Decode a tenant-issued JWT against the tenant's Keycloak public key.

    Avoids the lib's private `_decode_token` so we don't depend on internals."""
    try:
        payload = jwt.decode(
            token,
            idp.public_key,
            algorithms=["RS256"],
            audience=idp.client_id,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    return OIDCUser.model_validate(payload)


def get_current_user_dep():
    """Return a dependency that resolves the current user from the per-tenant idp."""

    async def _resolve(request: Request) -> OIDCUser:
        tenant = getattr(request.state, "tenant", None)
        if tenant is None or tenant.idp is None:
            return OIDCUser(
                sub="anonymous",
                iat=0,
                exp=0,
                email=None,
                email_verified=False,
                preferred_username="anonymous",
            )
        auth = request.headers.get("authorization") or ""
        if not auth.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing bearer token")
        token = auth.split(" ", 1)[1].strip()
        return verify_token(token, tenant.idp)

    return _resolve


async def _platform_jwks() -> dict:
    """Fetch + cache the platform Keycloak JWKS."""
    if not (global_settings.platform_keycloak_url and global_settings.platform_keycloak_realm):
        raise HTTPException(status_code=500, detail="Platform Keycloak not configured")
    cache_key = f"{global_settings.platform_keycloak_url}/{global_settings.platform_keycloak_realm}"
    now = time.monotonic()
    async with _platform_jwks_lock:
        cached = _platform_jwks_cache.get(cache_key)
        if cached and (now - cached[0]) < _PLATFORM_JWKS_TTL:
            return cached[1]
        url = (
            f"{global_settings.platform_keycloak_url.rstrip('/')}/realms/"
            f"{global_settings.platform_keycloak_realm}/protocol/openid-connect/certs"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            jwks = resp.json()
        _platform_jwks_cache[cache_key] = (now, jwks)
        return jwks


def _jwk_to_pem(jwk: dict) -> str:
    """Convert a single JWK dict to a PEM public key (uses pyjwt helpers)."""
    return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)


async def _verify_platform_token(token: str) -> Optional[str]:
    """Return actor id if `token` is a valid platform JWT with `platform-admin` role."""
    try:
        unverified = jwt.get_unverified_header(token)
    except jwt.PyJWTError:
        return None
    kid = unverified.get("kid")
    jwks = await _platform_jwks()
    keys = jwks.get("keys", [])
    matched = next((k for k in keys if k.get("kid") == kid), None)
    if matched is None:
        return None
    public_key = _jwk_to_pem(matched)
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[matched.get("alg") or "RS256"],
            audience=global_settings.platform_keycloak_client_id,
            options={"verify_aud": bool(global_settings.platform_keycloak_client_id)},
        )
    except jwt.PyJWTError:
        return None
    realm_roles = (payload.get("realm_access") or {}).get("roles") or []
    resource = (payload.get("resource_access") or {}).get(global_settings.platform_keycloak_client_id or "") or {}
    client_roles = resource.get("roles") or []
    if "platform-admin" not in realm_roles and "platform-admin" not in client_roles:
        return None
    return payload.get("preferred_username") or payload.get("sub") or "platform-admin"


async def verify_admin(
    request: Request,
    credentials: Optional[HTTPBasicCredentials] = Depends(_basic),
) -> str:
    """Authorize an admin caller via HTTP Basic and/or platform Keycloak.

    Either credential grants access; both are checked. Returns actor identifier."""
    actor: Optional[str] = None

    if credentials is not None and global_settings.admin_password:
        ok_user = secrets.compare_digest(credentials.username, global_settings.admin_user)
        ok_pass = secrets.compare_digest(credentials.password, global_settings.admin_password)
        if ok_user and ok_pass:
            actor = credentials.username

    if actor is None:
        auth = request.headers.get("authorization") or ""
        if auth.lower().startswith("bearer ") and global_settings.platform_keycloak_enabled:
            token = auth.split(" ", 1)[1].strip()
            actor = await _verify_platform_token(token)

    if actor is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": 'Basic, Bearer realm="platform"'},
        )

    request.state.user = actor
    return actor
