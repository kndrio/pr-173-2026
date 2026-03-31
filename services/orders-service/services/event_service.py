import json
import uuid
from typing import Any

import redis.asyncio as aioredis
import structlog

logger = structlog.get_logger()

_CHANNEL = "orders"


async def publish_order_event(
    redis: aioredis.Redis,  # type: ignore[type-arg]
    event_type: str,
    order_id: uuid.UUID,
    extra_data: dict[str, Any] | None = None,
) -> None:
    """Publish an order event as JSON to the 'orders' Redis Pub/Sub channel."""
    payload: dict[str, Any] = {
        "event_type": event_type,
        "order_id": str(order_id),
        **(extra_data or {}),
    }
    message = json.dumps(payload)
    await redis.publish(_CHANNEL, message)
    logger.info("event_published", event_type=event_type, order_id=str(order_id))
