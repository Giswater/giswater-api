"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging

logger = logging.getLogger(__name__)

# Single API-owned schema: basic-auth tables + audit log tables.
GWAPI_SCHEMA = "gwapi"

# DEPRECATED #26: pre-1.6.0 deployments kept audit logs in the `log` schema.
# The resolver below keeps reading/writing it until Alembic relocates the
# tables into `gwapi`. Remove in 2.0.0 (grep `DEPRECATED #26`).
LEGACY_LOG_SCHEMA = "log"

# Auth tables
GWAPI_USERS_TABLE = "users"
GWAPI_ROLES_TABLE = "roles"
GWAPI_USER_ROLES_TABLE = "user_roles"

# Audit log tables
GWAPI_LOG_TABLE = "gw_api_logs"
GWAPI_LOG_DB_TABLE = "gw_api_logs_db"

# Per-tenant cache of the resolved log schema. Cleared after a successful
# migration so the next request picks up `gwapi` (see migrate.run_alembic_upgrade).
_log_schema_cache: dict[str, str] = {}


def invalidate_log_schema_cache(tenant_id: str | None = None) -> None:
    if tenant_id is None:
        _log_schema_cache.clear()
    else:
        _log_schema_cache.pop(tenant_id, None)


async def _table_exists(conn, schema: str, table: str) -> bool:
    async with conn.cursor() as cursor:
        await cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
            (schema, table),
        )
        return await cursor.fetchone() is not None


async def _detect_log_schema(db_manager) -> str | None:
    """Return the schema that currently holds the audit log tables.

    Returns None when the database is unreachable so the caller can avoid
    caching a transient default.
    """
    async with db_manager.get_db() as conn:
        if conn is None:
            return None
        if await _table_exists(conn, GWAPI_SCHEMA, GWAPI_LOG_TABLE):
            return GWAPI_SCHEMA
        if await _table_exists(conn, LEGACY_LOG_SCHEMA, GWAPI_LOG_TABLE):
            logger.warning(
                "[%s] DEPRECATED #26: audit logs still in the 'log' schema; run "
                "'giswater-api db upgrade' to relocate them to 'gwapi'. Removal in 2.0.0.",
                db_manager.tenant_id,
            )
            return LEGACY_LOG_SCHEMA
    # Neither exists yet (e.g. fresh DB before migration); target gwapi.
    return GWAPI_SCHEMA


async def resolve_log_schema(db_manager) -> str:
    """Resolve which schema audit log reads/writes should target for a tenant.

    Prefers `gwapi`; falls back to the legacy `log` schema until migration has
    moved the tables. Result is cached per tenant.
    """
    tenant_id = db_manager.tenant_id
    cached = _log_schema_cache.get(tenant_id)
    if cached is not None:
        return cached
    schema = await _detect_log_schema(db_manager)
    if schema is None:
        # DB transiently unavailable; do not cache the optimistic default.
        return GWAPI_SCHEMA
    _log_schema_cache[tenant_id] = schema
    return schema
