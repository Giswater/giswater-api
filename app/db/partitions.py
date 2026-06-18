"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging
from datetime import datetime, timezone

from psycopg import sql

from .schema import DB_LOG_TABLE, HTTP_LOG_TABLE, LEGACY_DB_LOG_TABLE, LEGACY_HTTP_LOG_TABLE, LogTargets

logger = logging.getLogger(__name__)


def _month_range(ts: datetime, table_name: str) -> tuple[datetime, datetime, str]:
    month_start = datetime(ts.year, ts.month, 1, tzinfo=ts.tzinfo)
    if ts.month == 12:
        month_end = datetime(ts.year + 1, 1, 1, tzinfo=ts.tzinfo)
    else:
        month_end = datetime(ts.year, ts.month + 1, 1, tzinfo=ts.tzinfo)
    partition_name = f"{table_name}_{month_start.year}_{month_start.month:02d}"
    return month_start, month_end, partition_name


def _candidate_partition_names(table_name: str, partition_name: str) -> tuple[str, ...]:
    """Names a monthly partition may already have (current or legacy prefix)."""
    if table_name == HTTP_LOG_TABLE:
        legacy = partition_name.replace(f"{HTTP_LOG_TABLE}_", f"{LEGACY_HTTP_LOG_TABLE}_", 1)
        return (partition_name, legacy)
    if table_name == DB_LOG_TABLE:
        legacy = partition_name.replace(f"{DB_LOG_TABLE}_", f"{LEGACY_DB_LOG_TABLE}_", 1)
        return (partition_name, legacy)
    return (partition_name,)


async def _partition_table_exists(conn, schema: str, name: str) -> bool:
    async with conn.cursor() as cursor:
        await cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
            (schema, name),
        )
        return await cursor.fetchone() is not None


async def ensure_log_partition(conn, ts: datetime, table_name: str, schema: str) -> None:
    """Create the monthly partition for `ts` if it does not already exist."""
    month_start, month_end, partition_name = _month_range(ts, table_name)
    for name in _candidate_partition_names(table_name, partition_name):
        if await _partition_table_exists(conn, schema, name):
            return
    async with conn.cursor() as cursor:
        await cursor.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.{}
                PARTITION OF {}.{}
                FOR VALUES FROM ({}) TO ({})
                """
            ).format(
                sql.Identifier(schema),
                sql.Identifier(partition_name),
                sql.Identifier(schema),
                sql.Identifier(table_name),
                sql.Literal(month_start),
                sql.Literal(month_end),
            ),
        )


async def ensure_current_month_partitions(db_manager, targets: LogTargets) -> None:
    """Ensure the current-month partitions exist for both audit log tables."""
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        now = datetime.now(timezone.utc)
        try:
            await ensure_log_partition(conn, now, targets.http_table, targets.schema)
            await ensure_log_partition(conn, now, targets.db_table, targets.schema)
            await conn.commit()
        except Exception as exc:
            await conn.rollback()
            logger.warning("[%s] log partition init failed: %s", db_manager.tenant_id, exc)
