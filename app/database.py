"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import asyncio
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from fastapi import HTTPException

from .config import settings


class DatabaseManager:
    """Manages database connections using env configuration."""

    def __init__(self):
        """Initialize database manager with env-backed settings."""
        self.connection_pool = None

        # Get database settings from env
        self.host = settings.db_host
        self.port = settings.db_port
        self.dbname = settings.db_name
        self.user = settings.db_user
        self.password = settings.db_password
        self.default_schema = settings.db_schema

        # Database connection string (allow override)
        if settings.database_url:
            self.database_url = settings.database_url
        else:
            self.database_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}?application_name=giswater-api"

        # Pool is initialized on startup to avoid blocking at import time

    async def init_conn_pool(self):
        """Initialize the async connection pool."""
        try:
            self.connection_pool = AsyncConnectionPool(
                self.database_url,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
                timeout=settings.db_pool_timeout,
                max_waiting=settings.db_pool_max_waiting,
                max_idle=settings.db_pool_max_idle,
                open=False,
            )
            await asyncio.wait_for(self.connection_pool.open(), timeout=settings.db_connect_timeout)
            print(f"Initialized connection pool for {self.dbname}")
        except asyncio.TimeoutError:
            print(f"Timed out initializing connection pool for {self.dbname}")
            self.connection_pool = None
        except Exception as e:
            print(f"Failed to initialize connection pool for {self.dbname}: {e}")
            self.connection_pool = None

    @asynccontextmanager
    async def get_db(self):
        """
        Get a database connection from the pool.

        Yields:
            psycopg connection or None if connection fails
        """
        max_tries = 2
        n_try = 0
        while self.connection_pool is None and n_try < max_tries:
            await self.init_conn_pool()
            n_try += 1
            if self.connection_pool is None:
                await asyncio.sleep(5)

        if self.connection_pool is None:
            yield None
            return

        async with self.connection_pool.connection() as conn:
            yield conn

    async def validate_schema(self, schema: str) -> bool:
        """
        Validate if a schema exists in the database.

        Args:
            schema: Schema name to validate

        Returns:
            True if schema exists, False otherwise

        Raises:
            HTTPException: If database connection fails or query error occurs
        """
        async with self.get_db() as conn:
            if conn is None:
                raise HTTPException(status_code=500, detail="Database connection failed")
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", (schema,)
                    )
                    return await cursor.fetchone() is not None
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e

    async def close(self):
        """Close the connection pool."""
        if self.connection_pool:
            await self.connection_pool.close()
            print(f"Closed connection pool for {self.dbname}")
