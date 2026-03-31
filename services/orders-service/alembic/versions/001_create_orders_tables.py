"""Create orders table with JSONB items column

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
    # Create enums idempotently
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'orderstatus_enum') THEN
                CREATE TYPE orderstatus_enum AS ENUM (
                    'pendente', 'em_andamento', 'concluido', 'cancelado'
                );
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'priority_enum') THEN
                CREATE TYPE priority_enum AS ENUM (
                    'baixa', 'media', 'alta', 'urgente'
                );
            END IF;
        END $$;
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              UUID            PRIMARY KEY,
            customer_name   VARCHAR(255)    NOT NULL,
            customer_email  VARCHAR(255)    NOT NULL,
            description     TEXT            NOT NULL,
            items           JSONB           NOT NULL DEFAULT '[]'::jsonb,
            total_amount    NUMERIC(10, 2)  NOT NULL DEFAULT 0.00,
            status          orderstatus_enum NOT NULL DEFAULT 'pendente',
            priority        priority_enum   NOT NULL DEFAULT 'media',
            notes           TEXT,
            created_by      UUID            NOT NULL,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_status     ON orders (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_priority   ON orders (priority)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_created_at ON orders (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_created_by ON orders (created_by)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_orders_created_by")
    op.execute("DROP INDEX IF EXISTS ix_orders_created_at")
    op.execute("DROP INDEX IF EXISTS ix_orders_priority")
    op.execute("DROP INDEX IF EXISTS ix_orders_status")
    op.execute("DROP TABLE  IF EXISTS orders")
    op.execute("DROP TYPE   IF EXISTS orderstatus_enum")
    op.execute("DROP TYPE   IF EXISTS priority_enum")
