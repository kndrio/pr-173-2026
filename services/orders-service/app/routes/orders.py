import math
import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import RedisCache, get_cache
from app.core.database import get_db
from app.core.security import UserPayload, get_current_user
from app.models import Order, OrderStatus, Priority, VALID_TRANSITIONS
from app.schemas import OrderCreate, OrderListResponse, OrderResponse, OrderUpdate
from app.core.events import publish_order_event

logger = structlog.get_logger()

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

# Cache key helpers
_LIST_PATTERN = "orders:list:*"


def _list_key(page: int, page_size: int, status: str | None, priority: str | None) -> str:
    return f"orders:list:{page}:{page_size}:{status or 'all'}:{priority or 'all'}"


def _detail_key(order_id: uuid.UUID) -> str:
    return f"orders:detail:{order_id}"


@router.get("", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    priority_filter: Priority | None = Query(default=None, alias="priority"),
    _user: UserPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_cache),
) -> OrderListResponse:
    """List orders with pagination and optional filters. Served from cache when available."""
    cache_key = _list_key(
        page,
        page_size,
        status_filter.value if status_filter else None,
        priority_filter.value if priority_filter else None,
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return OrderListResponse.model_validate(cached)

    query = select(Order)
    if status_filter is not None:
        query = query.where(Order.status == status_filter)
    if priority_filter is not None:
        query = query.where(Order.priority == priority_filter)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total: int = count_result.scalar_one()

    rows = await db.execute(
        query.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    orders = list(rows.scalars().all())

    result = OrderListResponse(
        items=[OrderResponse.model_validate(o) for o in orders],
        total_count=total,
        page=page,
        page_size=page_size,
    )
    await cache.set(cache_key, result.model_dump(mode="json"))
    return result


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    user: UserPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_cache),
) -> OrderResponse:
    """Create a new order. Invalidates list cache and publishes order_created event."""
    items_json = [
        {
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
        }
        for item in body.items
    ]

    order = Order(
        customer_name=body.customer_name,
        customer_email=str(body.customer_email),
        description=body.description,
        items=items_json,
        total_amount=body.total_amount,
        priority=body.priority,
        notes=body.notes,
        created_by=user.id,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    await cache.delete_pattern(_LIST_PATTERN)
    await publish_order_event(cache.client, "order_created", order.id, {"status": order.status.value})

    logger.info("order_created", order_id=str(order.id), total=str(order.total_amount))
    return OrderResponse.model_validate(order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    _user: UserPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_cache),
) -> OrderResponse:
    """Get a single order by ID. Served from cache when available."""
    cache_key = _detail_key(order_id)
    cached = await cache.get(cache_key)
    if cached is not None:
        return OrderResponse.model_validate(cached)

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    response = OrderResponse.model_validate(order)
    await cache.set(cache_key, response.model_dump(mode="json"))
    return response


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: uuid.UUID,
    body: OrderUpdate,
    user: UserPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_cache),
) -> OrderResponse:
    """
    Update order status, priority, or notes.
    NOTE: per MVP spec, no ownership isolation — any authenticated user may update any order.
    The `user` parameter is kept (not prefixed `_`) to signal it is used for auth, not ignored.
    Status transitions are validated against the state machine.
    Invalidates both list and detail caches. Publishes order_updated event.
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if body.status is not None:
        allowed = VALID_TRANSITIONS.get(order.status, set())
        if body.status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status transition: {order.status.value} → {body.status.value}",
            )
        order.status = body.status

    if body.priority is not None:
        order.priority = body.priority

    if body.notes is not None:
        order.notes = body.notes

    await db.commit()
    await db.refresh(order)

    await cache.delete(_detail_key(order_id))
    await cache.delete_pattern(_LIST_PATTERN)
    await publish_order_event(cache.client, "order_updated", order.id, {"status": order.status.value})

    logger.info("order_updated", order_id=str(order.id))
    return OrderResponse.model_validate(order)
