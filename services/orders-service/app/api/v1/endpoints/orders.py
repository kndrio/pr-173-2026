import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as aioredis

from app.core.database import get_db
from app.core.redis import get_redis
from app.dependencies import get_current_user_id
from app.models.order import OrderStatus, Priority
from app.schemas.order import (
    AIAnalysisResponse,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from services.cache_service import get_orders_cache, invalidate_orders_cache, set_orders_cache
from services.event_service import publish_order_event
from services.order_service import create_order, get_order, list_orders, update_order_status

logger = structlog.get_logger()

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    data: OrderCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),  # type: ignore[type-arg]
) -> OrderResponse:
    """Create a new order. Invalidates cache and publishes order_created event."""
    order = await create_order(db, data, user_id)
    await invalidate_orders_cache(redis)
    await publish_order_event(redis, "order_created", order.id, {"status": order.status.value})
    return OrderResponse.model_validate(order)


@router.get("", response_model=OrderListResponse)
async def list_orders_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    priority_filter: Priority | None = Query(default=None, alias="priority"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),  # type: ignore[type-arg]
) -> OrderListResponse:
    """List orders with pagination and optional filters. Served from Redis cache when available."""
    status_val = status_filter.value if status_filter else None
    priority_val = priority_filter.value if priority_filter else None

    cached = await get_orders_cache(redis, page, page_size, status_val, priority_val)
    if cached is not None:
        logger.info("orders_list_cache_hit")
        return OrderListResponse.model_validate(cached)

    result = await list_orders(db, page=page, page_size=page_size, status=status_filter, priority=priority_filter)
    await set_orders_cache(redis, page, page_size, status_val, priority_val, result.model_dump(mode="json"))
    return result


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Get a single order by ID with all items. Always fetches from DB."""
    order = await get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status_endpoint(
    order_id: uuid.UUID,
    body: OrderStatusUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),  # type: ignore[type-arg]
) -> OrderResponse:
    """Update order status with state machine validation. Invalidates cache and publishes event."""
    try:
        order = await update_order_status(db, order_id, body.status)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    await invalidate_orders_cache(redis)
    await publish_order_event(redis, "order_updated", order.id, {"status": order.status.value})
    return OrderResponse.model_validate(order)
