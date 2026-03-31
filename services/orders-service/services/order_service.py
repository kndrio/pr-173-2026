import math
import uuid
from decimal import Decimal

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem, OrderStatus, Priority, VALID_TRANSITIONS
from app.schemas.order import (
    OrderCreate,
    OrderFilters,
    OrderListItemResponse,
    OrderListResponse,
    PriorityCount,
    StatusCount,
)

logger = structlog.get_logger()


async def create_order(
    db: AsyncSession, data: OrderCreate, user_id: uuid.UUID
) -> Order:
    """Create a new order, computing subtotals and total_amount from items."""
    items: list[OrderItem] = []
    total_amount = Decimal("0.00")

    for item_data in data.items:
        subtotal = (item_data.quantity * item_data.unit_price).quantize(Decimal("0.01"))
        total_amount += subtotal
        items.append(
            OrderItem(
                name=item_data.name,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                subtotal=subtotal,
            )
        )

    order = Order(
        customer_name=data.customer_name,
        customer_email=str(data.customer_email),
        description=data.description,
        priority=data.priority,
        notes=data.notes,
        total_amount=total_amount.quantize(Decimal("0.01")),
        created_by=user_id,
        items=items,
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)
    logger.info("order_created", order_id=str(order.id), total_amount=str(order.total_amount))
    return order


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> Order | None:
    """Fetch a single order by ID (items loaded via selectin)."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def list_orders(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: OrderStatus | None = None,
    priority: Priority | None = None,
) -> OrderListResponse:
    """List orders with optional filters and pagination."""
    base_query = select(Order)
    if status is not None:
        base_query = base_query.where(Order.status == status)
    if priority is not None:
        base_query = base_query.where(Order.priority == priority)

    # Total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total: int = total_result.scalar_one()

    # Paginated results (ordered by created_at DESC)
    paginated = (
        base_query.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = await db.execute(paginated)
    orders = list(rows.scalars().all())

    pages = max(1, math.ceil(total / page_size)) if total > 0 else 1

    # Build filter counters (across the full unfiltered result set)
    status_counts = await _get_status_counts(db)
    priority_counts = await _get_priority_counts(db)

    return OrderListResponse(
        items=[OrderListItemResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        filters=OrderFilters(
            status_counts=status_counts,
            priority_counts=priority_counts,
        ),
    )


async def _get_status_counts(db: AsyncSession) -> list[StatusCount]:
    result = await db.execute(
        select(Order.status, func.count(Order.id).label("count")).group_by(Order.status)
    )
    return [StatusCount(status=row.status, count=row.count) for row in result.all()]


async def _get_priority_counts(db: AsyncSession) -> list[PriorityCount]:
    result = await db.execute(
        select(Order.priority, func.count(Order.id).label("count")).group_by(Order.priority)
    )
    return [PriorityCount(priority=row.priority, count=row.count) for row in result.all()]


async def update_order_status(
    db: AsyncSession, order_id: uuid.UUID, new_status: OrderStatus
) -> Order:
    """
    Update order status with state machine validation.
    Raises ValueError for invalid transitions, LookupError if order not found.
    """
    order = await get_order(db, order_id)
    if order is None:
        raise LookupError(f"Order {order_id} not found")

    allowed = VALID_TRANSITIONS.get(order.status, set())
    if new_status not in allowed:
        raise ValueError(
            f"Invalid status transition: {order.status.value} → {new_status.value}"
        )

    order.status = new_status
    await db.commit()
    await db.refresh(order)
    logger.info(
        "order_status_updated",
        order_id=str(order.id),
        new_status=new_status.value,
    )
    return order
