"""Rename legacy monthly log partitions after parent table renames

Revision ID: 0003_log_partition_names
Revises: 0002_log_tables
Create Date: 2026-06-17

Revision 0002 renamed the partitioned parents to `http_logs` / `db_logs` but
left child tables named `gw_api_logs_YYYY_MM` / `gw_api_logs_db_YYYY_MM`. Runtime
partition creation then collides on the same month range. This revision renames
those child partitions to match the parent names. Idempotent.
"""

from alembic import op

revision = "0003_log_partition_names"
down_revision = "0002_log_tables"
branch_labels = None
depends_on = None

HTTP_LOG_TABLE = "http_logs"
DB_LOG_TABLE = "db_logs"


def _rename_log_partitions_sql(schema: str) -> str:
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


def upgrade() -> None:
    op.execute(_rename_log_partitions_sql("gwapi"))


def downgrade() -> None:
    pass
