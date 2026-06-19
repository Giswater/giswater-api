"""gwapi initial: schema, auth tables, and audit logs

Revision ID: 0001_gwapi_initial
Revises:
Create Date: 2026-06-17

Creates the `gwapi` schema, basic-auth tables (roles, users, user_roles), and
audit log tables (`http_logs`, `db_logs`).

On existing 1.4.0 deployments the auth tables already live in `gwapi` and the
audit tables live in the `log` schema as `gw_api_logs` / `gw_api_logs_db`. This
revision relocates those log tables (with partitions and indexes) into `gwapi`,
renames them, preserves all historical rows, then drops the now-empty `log`
schema. On a fresh install there is no `log` schema, so the log tables are
created directly in `gwapi`. Every statement is idempotent.
"""

from alembic import op

revision = "0001_gwapi_initial"
down_revision = None
branch_labels = None
depends_on = None

LEGACY_LOG_TABLES = ("gw_api_logs", "gw_api_logs_db")
HTTP_LOG_TABLE = "http_logs"
DB_LOG_TABLE = "db_logs"


def _relocate_sql(src_schema: str, dst_schema: str) -> str:
    """PL/pgSQL that moves both partitioned log tables from src to dst.

    Child partitions are separate tables and are NOT moved automatically by
    `ALTER TABLE ... SET SCHEMA` on the parent, so they are moved explicitly
    first. Owned sequences and indexes move with their table.
    """
    tables = ", ".join(f"'{t}'" for t in LEGACY_LOG_TABLES)
    return f"""
    DO $$
    DECLARE
        part record;
        parent text;
    BEGIN
        FOREACH parent IN ARRAY ARRAY[{tables}]
        LOOP
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = '{src_schema}' AND table_name = parent
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = '{dst_schema}' AND table_name = parent
            ) THEN
                FOR part IN
                    SELECT c.relname AS name
                    FROM pg_inherits i
                    JOIN pg_class c ON c.oid = i.inhrelid
                    JOIN pg_class p ON p.oid = i.inhparent
                    JOIN pg_namespace np ON np.oid = p.relnamespace
                    JOIN pg_namespace nc ON nc.oid = c.relnamespace
                    WHERE np.nspname = '{src_schema}'
                      AND nc.nspname = '{src_schema}'
                      AND p.relname = parent
                LOOP
                    EXECUTE format('ALTER TABLE {src_schema}.%I SET SCHEMA {dst_schema}', part.name);
                END LOOP;
                EXECUTE format('ALTER TABLE {src_schema}.%I SET SCHEMA {dst_schema}', parent);
            END IF;
        END LOOP;
    END $$;
    """


def _rename_migrated_tables_sql(schema: str) -> str:
    """Rename relocated legacy tables to their current names."""
    return f"""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = 'gw_api_logs'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = '{HTTP_LOG_TABLE}'
        ) THEN
            EXECUTE format('ALTER TABLE {schema}.gw_api_logs RENAME TO {HTTP_LOG_TABLE}');
        END IF;
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = 'gw_api_logs_db'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = '{DB_LOG_TABLE}'
        ) THEN
            EXECUTE format('ALTER TABLE {schema}.gw_api_logs_db RENAME TO {DB_LOG_TABLE}');
        END IF;
    END $$;
    """


def _rename_log_partitions_sql(schema: str) -> str:
    """Rename child partitions that still use legacy prefixes after parent renames."""
    return f"""
    DO $$
    DECLARE
        part record;
        new_name text;
    BEGIN
        FOR part IN
            SELECT c.relname AS name
            FROM pg_inherits i
            JOIN pg_class c ON c.oid = i.inhrelid
            JOIN pg_class p ON p.oid = i.inhparent
            JOIN pg_namespace n ON n.oid = p.relnamespace
            WHERE n.nspname = '{schema}'
              AND p.relname = '{HTTP_LOG_TABLE}'
              AND c.relname LIKE 'gw_api_logs_%'
              AND c.relname NOT LIKE 'gw_api_logs_db_%'
        LOOP
            new_name := replace(part.name, 'gw_api_logs', '{HTTP_LOG_TABLE}');
            IF new_name <> part.name AND NOT EXISTS (
                SELECT 1 FROM pg_class c2
                JOIN pg_namespace n2 ON n2.oid = c2.relnamespace
                WHERE n2.nspname = '{schema}' AND c2.relname = new_name
            ) THEN
                EXECUTE format('ALTER TABLE {schema}.%I RENAME TO %I', part.name, new_name);
            END IF;
        END LOOP;

        FOR part IN
            SELECT c.relname AS name
            FROM pg_inherits i
            JOIN pg_class c ON c.oid = i.inhrelid
            JOIN pg_class p ON p.oid = i.inhparent
            JOIN pg_namespace n ON n.oid = p.relnamespace
            WHERE n.nspname = '{schema}'
              AND p.relname = '{DB_LOG_TABLE}'
              AND c.relname LIKE 'gw_api_logs_db_%'
        LOOP
            new_name := replace(part.name, 'gw_api_logs_db', '{DB_LOG_TABLE}');
            IF new_name <> part.name AND NOT EXISTS (
                SELECT 1 FROM pg_class c2
                JOIN pg_namespace n2 ON n2.oid = c2.relnamespace
                WHERE n2.nspname = '{schema}' AND c2.relname = new_name
            ) THEN
                EXECUTE format('ALTER TABLE {schema}.%I RENAME TO %I', part.name, new_name);
            END IF;
        END LOOP;
    END $$;
    """


def _rename_tables_back_sql(schema: str) -> str:
    """Downgrade helper: restore legacy table names before relocating back to `log`."""
    return f"""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = '{HTTP_LOG_TABLE}'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = 'gw_api_logs'
        ) THEN
            EXECUTE format('ALTER TABLE {schema}.{HTTP_LOG_TABLE} RENAME TO gw_api_logs');
        END IF;
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = '{DB_LOG_TABLE}'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = 'gw_api_logs_db'
        ) THEN
            EXECUTE format('ALTER TABLE {schema}.{DB_LOG_TABLE} RENAME TO gw_api_logs_db');
        END IF;
    END $$;
    """


def _create_log_tables_sql(schema: str) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS {schema}.{HTTP_LOG_TABLE} (
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
    ) PARTITION BY RANGE (ts);

    CREATE INDEX IF NOT EXISTS http_logs_ts_idx ON {schema}.{HTTP_LOG_TABLE} (ts DESC);
    CREATE INDEX IF NOT EXISTS http_logs_endpoint_idx ON {schema}.{HTTP_LOG_TABLE} (endpoint);
    CREATE INDEX IF NOT EXISTS http_logs_method_idx ON {schema}.{HTTP_LOG_TABLE} (method);
    CREATE INDEX IF NOT EXISTS http_logs_status_idx ON {schema}.{HTTP_LOG_TABLE} (status);
    CREATE INDEX IF NOT EXISTS http_logs_user_idx ON {schema}.{HTTP_LOG_TABLE} (user_name);
    CREATE INDEX IF NOT EXISTS http_logs_request_id_idx ON {schema}.{HTTP_LOG_TABLE} (request_id);

    CREATE TABLE IF NOT EXISTS {schema}.{DB_LOG_TABLE} (
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
    ) PARTITION BY RANGE (ts);

    CREATE INDEX IF NOT EXISTS db_logs_ts_idx ON {schema}.{DB_LOG_TABLE} (ts DESC);
    CREATE INDEX IF NOT EXISTS db_logs_request_id_idx ON {schema}.{DB_LOG_TABLE} (request_id);
    """


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS gwapi")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS gwapi.roles (
            name text PRIMARY KEY,
            description text
        )
        """
    )
    op.execute(
        """
        INSERT INTO gwapi.roles (name, description) VALUES
            ('role_basic', 'Basic read access'),
            ('role_edit', 'Edit access'),
            ('role_om', 'Operations and maintenance'),
            ('role_epa', 'EPA / scenario access'),
            ('role_master', 'Master access')
        ON CONFLICT (name) DO NOTHING
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS gwapi.users (
            id bigserial PRIMARY KEY,
            username text NOT NULL UNIQUE,
            password_hash text NOT NULL,
            db_role text NOT NULL,
            enabled boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS gwapi_users_username_idx ON gwapi.users (username)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS gwapi.user_roles (
            user_id bigint NOT NULL REFERENCES gwapi.users (id) ON DELETE CASCADE,
            role_name text NOT NULL REFERENCES gwapi.roles (name) ON DELETE CASCADE,
            PRIMARY KEY (user_id, role_name)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS gwapi_user_roles_user_id_idx ON gwapi.user_roles (user_id)")

    # Move legacy `log.*` tables into `gwapi` (no-op on fresh installs).
    op.execute(_relocate_sql("log", "gwapi"))
    # Rename relocated tables to their current names (no-op when already renamed).
    op.execute(_rename_migrated_tables_sql("gwapi"))
    op.execute(_rename_log_partitions_sql("gwapi"))
    # Create the tables when they were not relocated (fresh install). Existing
    # (moved/renamed) tables and their indexes are skipped via IF NOT EXISTS.
    op.execute(_create_log_tables_sql("gwapi"))
    # Drop the legacy schema only if it is now empty; tolerate leftovers.
    op.execute(
        """
        DO $$
        BEGIN
            BEGIN
                DROP SCHEMA log RESTRICT;
            EXCEPTION WHEN OTHERS THEN
                NULL;  -- schema absent or still holds non-API objects
            END;
        END $$;
        """
    )


def downgrade() -> None:
    # Emergency rollback: move audit logs back to `log`, then drop auth tables.
    op.execute("CREATE SCHEMA IF NOT EXISTS log")
    op.execute(_rename_tables_back_sql("gwapi"))
    op.execute(_relocate_sql("gwapi", "log"))
    op.execute("DROP TABLE IF EXISTS gwapi.user_roles")
    op.execute("DROP TABLE IF EXISTS gwapi.users")
    op.execute("DROP TABLE IF EXISTS gwapi.roles")
