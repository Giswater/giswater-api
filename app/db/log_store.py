"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging
from typing import Any, Dict

from psycopg import sql
from psycopg.types.json import Json

from .partitions import ensure_log_partition
from .schema import GWAPI_LOG_DB_TABLE, GWAPI_LOG_TABLE, resolve_log_schema

logger = logging.getLogger(__name__)


async def insert_api_log(db_manager, record: Dict[str, Any]) -> None:
    schema = await resolve_log_schema(db_manager)
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        try:
            await ensure_log_partition(conn, record["ts"], GWAPI_LOG_TABLE, schema)
            async with conn.cursor() as cursor:
                await cursor.execute(
                    sql.SQL(
                        """
                        INSERT INTO {}.{} (
                            ts,
                            method,
                            endpoint,
                            status,
                            duration_ms,
                            user_name,
                            request_id,
                            client_ip,
                            query_params,
                            body_size,
                            response_size,
                            request_headers,
                            request_body,
                            response_headers,
                            response_body
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                    ).format(sql.Identifier(schema), sql.Identifier(GWAPI_LOG_TABLE)),
                    (
                        record.get("ts"),
                        record.get("method"),
                        record.get("endpoint"),
                        record.get("status"),
                        record.get("duration_ms"),
                        record.get("user_name"),
                        record.get("request_id"),
                        record.get("client_ip"),
                        Json(record.get("query_params")) if record.get("query_params") is not None else None,
                        record.get("body_size"),
                        record.get("response_size"),
                        Json(record.get("request_headers")) if record.get("request_headers") is not None else None,
                        record.get("request_body"),
                        Json(record.get("response_headers")) if record.get("response_headers") is not None else None,
                        record.get("response_body"),
                    ),
                )
            await conn.commit()
        except Exception:
            await conn.rollback()


async def insert_api_db_log(db_manager, record: Dict[str, Any]) -> None:
    schema = await resolve_log_schema(db_manager)
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        try:
            await ensure_log_partition(conn, record["ts"], GWAPI_LOG_DB_TABLE, schema)
            async with conn.cursor() as cursor:
                await cursor.execute(
                    sql.SQL(
                        """
                        INSERT INTO {}.{} (
                            ts,
                            request_id,
                            schema_name,
                            function_name,
                            sql_text,
                            response_json,
                            duration_ms,
                            status,
                            error
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                    ).format(sql.Identifier(schema), sql.Identifier(GWAPI_LOG_DB_TABLE)),
                    (
                        record.get("ts"),
                        record.get("request_id"),
                        record.get("schema_name"),
                        record.get("function_name"),
                        record.get("sql_text"),
                        record.get("response_json"),
                        record.get("duration_ms"),
                        record.get("status"),
                        record.get("error"),
                    ),
                )
            await conn.commit()
        except Exception:
            await conn.rollback()
