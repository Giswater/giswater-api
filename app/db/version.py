"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import psycopg
from fastapi import HTTPException
from psycopg import sql

from ..core.exceptions import DatabaseUnavailableError


async def get_db_version(log, db_manager, schema: str | None = None) -> str | None:
    """
    Return latest giswater version from sys_version.
    """
    schema_name = schema or db_manager.default_schema
    if schema_name is None:
        log.warning("Schema is None")
        raise HTTPException(status_code=500, detail="Schema not found")

    if not await db_manager.validate_schema(schema_name):
        log.warning(f"Schema '{schema_name}' not found")
        raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

    query = sql.SQL("SELECT giswater FROM {}.sys_version ORDER BY id DESC LIMIT 1").format(sql.Identifier(schema_name))
    async with db_manager.get_db() as conn:
        if conn is None:
            log.error("No connection to database")
            raise DatabaseUnavailableError()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                row = await cursor.fetchone()
            await conn.commit()
        except psycopg.Error as e:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(e)) from e

    if not row:
        return None
    return row[0]
