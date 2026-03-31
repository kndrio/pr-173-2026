import enum
import uuid
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    DateTime,
    Enum,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Priority(str, enum.Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"
    urgente = "urgente"


class OrderStatus(str, enum.Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluido = "concluido"
    cancelado = "cancelado"


# State machine: allowed transitions (data-model.md)
VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.pendente: {OrderStatus.em_andamento, OrderStatus.cancelado},
    OrderStatus.em_andamento: {OrderStatus.concluido, OrderStatus.cancelado},
    OrderStatus.concluido: set(),   # final — no exit
    OrderStatus.cancelado: set(),   # final — no exit
}


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Items stored as JSONB on PostgreSQL, JSON/TEXT on SQLite (tests)
    items: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    total_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00")
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="orderstatus_enum", create_type=False),
        nullable=False,
        default=OrderStatus.pendente,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority_enum", create_type=False),
        nullable=False,
        default=Priority.media,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_orders_status", "status"),
        Index("ix_orders_priority", "priority"),
        Index("ix_orders_created_at", "created_at"),
        Index("ix_orders_created_by", "created_by"),
    )
