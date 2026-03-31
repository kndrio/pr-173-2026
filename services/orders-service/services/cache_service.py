import json
from typing import Any

import redis.asyncio as aioredis
import structlog

from app.core.config import settings

logger = structlog.get_logger()

_CACHE_PREFIX = "orders:list:"


def _build_key(page: int, page_size: int, status: str | None, priority: str | None) -> str:
    return f"{_CACHE_PREFIX}{page}:{page_size}:{status or 'all'}:{priority or 'all'}"


async def get_orders_cache(
    redis: aioredis.Redis,  # type: ignore[type-arg]
    page: int,
    page_size: int,
    status: str | None,
    priority: str | None,
) -> Any | None:
    """Return cached JSON data or None if cache miss."""
    key = _build_key(page, page_size, status, priority)
    data = await redis.get(key)
    if data is not None:
        logger.debug("cache_hit", key=key)
        return json.loads(data)
    logger.debug("cache_miss", key=key)
    return None


async def set_orders_cache(
    redis: aioredis.Redis,  # type: ignore[type-arg]
    page: int,
    page_size: int,
    status: str | None,
    priority: str | None,
    data: Any,
) -> None:
    """Persist data in cache with configured TTL."""
    key = _build_key(page, page_size, status, priority)
    await redis.set(key, json.dumps(data), ex=settings.redis_cache_ttl)
    logger.debug("cache_set", key=key, ttl=settings.redis_cache_ttl)


async def invalidate_orders_cache(redis: aioredis.Redis) -> None:  # type: ignore[type-arg]
    """Delete all orders list cache keys using SCAN (avoids KEYS * in production)."""
    pattern = f"{_CACHE_PREFIX}*"
    cursor: int = 0
    deleted = 0
    while True:
        cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            await redis.delete(*keys)
            deleted += len(keys)
        if cursor == 0:
            break
    logger.debug("cache_invalidated", deleted=deleted)
