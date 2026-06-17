"""gwapi initial: schema + auth tables

Revision ID: 0001_gwapi_initial
Revises:
Create Date: 2026-06-17

Creates the `gwapi` schema and the basic-auth tables (roles, users, user_roles)
with their default role seed. These already lived in `gwapi` on 1.4.0, so every
statement is idempotent and a no-op against an existing deployment.
"""

from alembic import op

revision = "0001_gwapi_initial"
down_revision = None
branch_labels = None
depends_on = None


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


def downgrade() -> None:
    # Emergency only: drops auth tables but leaves the `gwapi` schema in place
    # (it may still hold the audit log tables and the Alembic version table).
    op.execute("DROP TABLE IF EXISTS gwapi.user_roles")
    op.execute("DROP TABLE IF EXISTS gwapi.users")
    op.execute("DROP TABLE IF EXISTS gwapi.roles")
