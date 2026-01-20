"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import psycopg2
import psycopg2.pool
from contextlib import contextmanager
from time import sleep
from fastapi import HTTPException

from .config import Config


class DatabaseManager:
    """Manages database connections for a specific client configuration."""

    def __init__(self, config: Config):
        """
        Initialize database manager with a specific config.

        Args:
            config: Config instance for this database
        """
        self.config = config
        self.connection_pool = None

        # Get database settings from config
        self.host = config.get_str("database", "host")
        self.port = config.get_str("database", "port")
        self.dbname = config.get_str("database", "db")
        self.user = config.get_str("database", "user")
        self.password = config.get_str("database", "password")
        self.default_schema = config.get_str("database", "schema")

        # Database connection string
        self.database_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

        # Initialize connection pool
        self.init_conn_pool()

    def init_conn_pool(self):
        """Initialize the connection pool."""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,  # Minimum number of connections
                10,  # Maximum number of connections
                self.database_url,
            )
            print(f"Initialized connection pool for {self.dbname}")
        except Exception as e:
            print(f"Failed to initialize connection pool for {self.dbname}: {e}")
            self.connection_pool = None

    @contextmanager
    def get_db(self):
        """
        Get a database connection from the pool.

        Yields:
            psycopg2 connection or None if connection fails
        """
        max_tries = 2
        n_try = 0
        while self.connection_pool is None and n_try < max_tries:
            self.init_conn_pool()
            n_try += 1
            if self.connection_pool is None:
                sleep(5)

        if self.connection_pool is None:
            yield None
            return

        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)

    def validate_schema(self, schema: str) -> bool:
        """
        Validate if a schema exists in the database.

        Args:
            schema: Schema name to validate

        Returns:
            True if schema exists, False otherwise

        Raises:
            HTTPException: If database connection fails or query error occurs
        """
        with self.get_db() as conn:
            if conn is None:
                raise HTTPException(status_code=500, detail="Database connection failed")
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", (schema,)
                    )
                    return cursor.fetchone() is not None
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e

    def close(self):
        """Close the connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print(f"Closed connection pool for {self.dbname}")
