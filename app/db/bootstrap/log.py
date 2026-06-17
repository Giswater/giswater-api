"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging
from datetime import datetime, timezone

from psycopg import sql

logger = logging.getLogger(__name__)

LOG_SCHEMA = "log"
LOG_TABLE = "gw_api_logs"
LOG_DB_TABLE = "gw_api_logs_db"


async def ensure_log_schema(db_manager) -> None:
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(LOG_SCHEMA)))
                await cursor.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.{} (
                            ts timestamptz NOT NULL,
                            id bigserial NOT NULL,
                            method text NOT NULL,
                            endpoint text NOT NULL,
                            status integer NOT NULL,
                            duration_ms integer,
                            user_name text,
                            request_id uuid,
                            client_ip inet,
                            query_params jsonb,
                            body_size integer,
                            response_size integer,
                            request_headers jsonb,
                            request_body text,
                            response_headers jsonb,
                            response_body text,
                            PRIMARY KEY (ts, id)
                        ) PARTITION BY RANGE (ts)
                        """
                    ).format(sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE))
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS request_headers jsonb").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS request_body text").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS response_headers jsonb").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS response_body text").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} DROP COLUMN IF EXISTS user_agent").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (ts DESC)").format(
                        sql.Identifier("gw_api_logs_ts_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (endpoint)").format(
                        sql.Identifier("gw_api_logs_endpoint_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (method)").format(
                        sql.Identifier("gw_api_logs_method_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (status)").format(
                        sql.Identifier("gw_api_logs_status_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (user_name)").format(
                        sql.Identifier("gw_api_logs_user_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (request_id)").format(
                        sql.Identifier("gw_api_logs_request_id_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.{} (
                            ts timestamptz NOT NULL,
                            id bigserial NOT NULL,
                            request_id uuid,
                            schema_name text,
                            function_name text,
                            sql_text text,
                            response_json text,
                            duration_ms integer,
                            status text,
                            error text,
                            PRIMARY KEY (ts, id)
                        ) PARTITION BY RANGE (ts)
                        """
                    ).format(sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_DB_TABLE))
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (ts DESC)").format(
                        sql.Identifier("gw_api_logs_db_ts_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_DB_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (request_id)").format(
                        sql.Identifier("gw_api_logs_db_request_id_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_DB_TABLE),
                    )
                )
            await conn.commit()
            await ensure_log_partition(conn, datetime.now(timezone.utc), LOG_TABLE)
            await ensure_log_partition(conn, datetime.now(timezone.utc), LOG_DB_TABLE)
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise


def _month_range(ts: datetime, table_name: str) -> tuple[datetime, datetime, str]:
    month_start = datetime(ts.year, ts.month, 1, tzinfo=ts.tzinfo)
    if ts.month == 12:
        month_end = datetime(ts.year + 1, 1, 1, tzinfo=ts.tzinfo)
    else:
        month_end = datetime(ts.year, ts.month + 1, 1, tzinfo=ts.tzinfo)
    partition_name = f"{table_name}_{month_start.year}_{month_start.month:02d}"
    return month_start, month_end, partition_name


async def ensure_log_partition(conn, ts: datetime, table_name: str) -> None:
    month_start, month_end, partition_name = _month_range(ts, table_name)
    async with conn.cursor() as cursor:
        await cursor.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.{}
                PARTITION OF {}.{}
                FOR VALUES FROM ({}) TO ({})
                """
            ).format(
                sql.Identifier(LOG_SCHEMA),
                sql.Identifier(partition_name),
                sql.Identifier(LOG_SCHEMA),
                sql.Identifier(table_name),
                sql.Literal(month_start),
                sql.Literal(month_end),
            ),
        )
