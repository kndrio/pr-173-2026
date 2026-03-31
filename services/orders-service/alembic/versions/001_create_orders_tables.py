"""Create orders and order_items tables

Revision ID: 001
Revises:
Create Date: 2026-03-30

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    priority_enum = postgresql.ENUM(
        "baixa", "media", "alta", "urgente", name="priority_enum", create_type=False
    )
    orderstatus_enum = postgresql.ENUM(
        "pendente", "em_andamento", "concluido", "cancelado",
        name="orderstatus_enum", create_type=False
    )
    priority_enum.create(op.get_bind(), checkfirst=True)
    orderstatus_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("customer_email", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column(
            "priority",
            sa.Enum("baixa", "media", "alta", "urgente", name="priority_enum"),
            nullable=False,
            server_default="media",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pendente", "em_andamento", "concluido", "cancelado",
                name="orderstatus_enum",
            ),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "total_amount",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_priority", "orders", ["priority"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])
    op.create_index("ix_orders_created_by", "orders", ["created_by"])

    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("quantity >= 1", name="ck_order_items_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="ck_order_items_unit_price_nonneg"),
        sa.CheckConstraint("subtotal >= 0", name="ck_order_items_subtotal_nonneg"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("orders")
    op.execute("DROP TYPE IF EXISTS orderstatus_enum")
    op.execute("DROP TYPE IF EXISTS priority_enum")
