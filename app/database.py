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
from .exceptions import DatabaseUnavailableError


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
        max_tries = 3
        retry_delay_seconds = 2

        for n_try in range(max_tries):
            if self.connection_pool is None:
                await self.init_conn_pool()
                if self.connection_pool is None:
                    if n_try < max_tries - 1:
                        await asyncio.sleep(retry_delay_seconds)
                    continue

            try:
                async with self.connection_pool.connection() as conn:
                    yield conn
                    return
            except Exception as e:
                print(f"Failed to acquire database connection (attempt {n_try + 1}/{max_tries}): {e}")
                # Pool may be stale after DB restarts/outages; force recreation.
                try:
                    if self.connection_pool is not None:
                        await self.connection_pool.close()
                except Exception:
                    pass
                self.connection_pool = None
                if n_try < max_tries - 1:
                    await asyncio.sleep(retry_delay_seconds)

        yield None

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
                raise DatabaseUnavailableError()
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", (schema,)
                    )
                    return await cursor.fetchone() is not None
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e

    async def is_db_available(self, timeout_seconds: float = 2.0) -> bool:
        """
        Fast one-shot availability check used by health endpoints.
        Returns quickly when DB is unavailable.
        """
        if self.connection_pool is None:
            try:
                await asyncio.wait_for(self.init_conn_pool(), timeout=timeout_seconds)
            except Exception:
                return False
            if self.connection_pool is None:
                return False

        try:
            async with self.connection_pool.connection(timeout=timeout_seconds) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
            return True
        except Exception:
            return False

    async def close(self):
        """Close the connection pool."""
        if self.connection_pool:
            await self.connection_pool.close()
            print(f"Closed connection pool for {self.dbname}")
