"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging

from psycopg import sql

logger = logging.getLogger(__name__)

GWAPI_SCHEMA = "gwapi"
GWAPI_USERS_TABLE = "users"
GWAPI_ROLES_TABLE = "roles"
GWAPI_USER_ROLES_TABLE = "user_roles"

GWAPI_DEFAULT_ROLES: tuple[tuple[str, str], ...] = (
    ("role_basic", "Basic read access"),
    ("role_edit", "Edit access"),
    ("role_om", "Operations and maintenance"),
    ("role_epa", "EPA / scenario access"),
    ("role_master", "Master access"),
)


async def ensure_gwapi_schema(db_manager) -> None:
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(GWAPI_SCHEMA)))
                await cursor.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.{} (
                            name text PRIMARY KEY,
                            description text
                        )
                        """
                    ).format(sql.Identifier(GWAPI_SCHEMA), sql.Identifier(GWAPI_ROLES_TABLE))
                )
                for role_name, description in GWAPI_DEFAULT_ROLES:
                    await cursor.execute(
                        sql.SQL(
                            """
                            INSERT INTO {}.{} (name, description)
                            VALUES (%s, %s)
                            ON CONFLICT (name) DO NOTHING
                            """
                        ).format(sql.Identifier(GWAPI_SCHEMA), sql.Identifier(GWAPI_ROLES_TABLE)),
                        (role_name, description),
                    )
                await cursor.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.{} (
                            id bigserial PRIMARY KEY,
                            username text NOT NULL UNIQUE,
                            password_hash text NOT NULL,
                            db_role text NOT NULL,
                            enabled boolean NOT NULL DEFAULT true,
                            created_at timestamptz NOT NULL DEFAULT now(),
                            updated_at timestamptz NOT NULL DEFAULT now()
                        )
                        """
                    ).format(sql.Identifier(GWAPI_SCHEMA), sql.Identifier(GWAPI_USERS_TABLE))
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (username)").format(
                        sql.Identifier("gwapi_users_username_idx"),
                        sql.Identifier(GWAPI_SCHEMA),
                        sql.Identifier(GWAPI_USERS_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.{} (
                            user_id bigint NOT NULL REFERENCES {}.{} (id) ON DELETE CASCADE,
                            role_name text NOT NULL REFERENCES {}.{} (name) ON DELETE CASCADE,
                            PRIMARY KEY (user_id, role_name)
                        )
                        """
                    ).format(
                        sql.Identifier(GWAPI_SCHEMA),
                        sql.Identifier(GWAPI_USER_ROLES_TABLE),
                        sql.Identifier(GWAPI_SCHEMA),
                        sql.Identifier(GWAPI_USERS_TABLE),
                        sql.Identifier(GWAPI_SCHEMA),
                        sql.Identifier(GWAPI_ROLES_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (user_id)").format(
                        sql.Identifier("gwapi_user_roles_user_id_idx"),
                        sql.Identifier(GWAPI_SCHEMA),
                        sql.Identifier(GWAPI_USER_ROLES_TABLE),
                    )
                )
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
