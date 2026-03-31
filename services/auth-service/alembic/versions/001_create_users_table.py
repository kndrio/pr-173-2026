"""create users table

Revision ID: 001
Revises:
Create Date: 2026-03-31

"""
from typing import Sequence, Union

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                CREATE TYPE user_role AS ENUM ('operator', 'manager', 'admin');
            END IF;
        END $$;
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          UUID         PRIMARY KEY,
            full_name   VARCHAR(255) NOT NULL,
            email       VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            role        user_role    NOT NULL DEFAULT 'operator',
            is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email     ON users (email)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_users_is_active ON users (is_active)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_is_active")
    op.execute("DROP INDEX IF EXISTS ix_users_email")
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TYPE  IF EXISTS user_role")
