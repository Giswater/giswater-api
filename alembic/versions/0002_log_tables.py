"""gwapi audit log tables (relocate legacy `log` schema or create fresh)

Revision ID: 0002_log_tables
Revises: 0001_gwapi_initial
Create Date: 2026-06-17

On existing 1.4.0 deployments the API audit tables live in the `log` schema.
This revision moves them (with their partitions and indexes) into `gwapi`,
preserving all historical rows, then drops the now-empty `log` schema. On a
fresh install there is no `log` schema, so the tables are created directly in
`gwapi`. Both paths are idempotent.
"""

from alembic import op

revision = "0002_log_tables"
down_revision = "0001_gwapi_initial"
branch_labels = None
depends_on = None

LOG_TABLES = ("gw_api_logs", "gw_api_logs_db")


def _relocate_sql(src_schema: str, dst_schema: str) -> str:
    """PL/pgSQL that moves both partitioned log tables from src to dst.

    Child partitions are separate tables and are NOT moved automatically by
    `ALTER TABLE ... SET SCHEMA` on the parent, so they are moved explicitly
    first. Owned sequences and indexes move with their table.
    """
    tables = ", ".join(f"'{t}'" for t in LOG_TABLES)
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


def _create_log_tables_sql(schema: str) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS {schema}.gw_api_logs (
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

    CREATE INDEX IF NOT EXISTS gw_api_logs_ts_idx ON {schema}.gw_api_logs (ts DESC);
    CREATE INDEX IF NOT EXISTS gw_api_logs_endpoint_idx ON {schema}.gw_api_logs (endpoint);
    CREATE INDEX IF NOT EXISTS gw_api_logs_method_idx ON {schema}.gw_api_logs (method);
    CREATE INDEX IF NOT EXISTS gw_api_logs_status_idx ON {schema}.gw_api_logs (status);
    CREATE INDEX IF NOT EXISTS gw_api_logs_user_idx ON {schema}.gw_api_logs (user_name);
    CREATE INDEX IF NOT EXISTS gw_api_logs_request_id_idx ON {schema}.gw_api_logs (request_id);

    CREATE TABLE IF NOT EXISTS {schema}.gw_api_logs_db (
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

    CREATE INDEX IF NOT EXISTS gw_api_logs_db_ts_idx ON {schema}.gw_api_logs_db (ts DESC);
    CREATE INDEX IF NOT EXISTS gw_api_logs_db_request_id_idx ON {schema}.gw_api_logs_db (request_id);
    """


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS gwapi")
    # Move legacy `log.*` tables into `gwapi` (no-op on fresh installs).
    op.execute(_relocate_sql("log", "gwapi"))
    # Create the tables when they were not relocated (fresh install). Existing
    # (moved) tables and their indexes are skipped via IF NOT EXISTS.
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
    # Emergency rollback: move the audit tables back to the `log` schema so a
    # previous (1.4.x) image can read/write them again.
    op.execute("CREATE SCHEMA IF NOT EXISTS log")
    op.execute(_relocate_sql("gwapi", "log"))
