import json
from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as aioredis
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Module-level connection pool — initialised at application startup
_redis_pool: aioredis.Redis | None = None  # type: ignore[type-arg]


async def init_redis_pool() -> None:
    """Create the shared Redis connection pool. Call once from app startup."""
    global _redis_pool
    _redis_pool = aioredis.from_url(settings.redis_url, decode_responses=True)


async def close_redis_pool() -> None:
    """Gracefully close the pool. Call from app shutdown."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None


class RedisCache:
    """Async Redis cache helper with JSON serialisation."""

    def __init__(self, client: aioredis.Redis) -> None:  # type: ignore[type-arg]
        self._client = client

    @property
    def client(self) -> aioredis.Redis:  # type: ignore[type-arg]
        """Expose the underlying client for Pub/Sub operations."""
        return self._client

    async def get(self, key: str) -> Any | None:
        raw = await self._client.get(key)
        if raw is None:
            logger.debug("cache_miss", key=key)
            return None
        logger.debug("cache_hit", key=key)
        return json.loads(raw)

    async def set(self, key: str, value: Any, ttl: int = settings.redis_cache_ttl) -> None:
        await self._client.set(key, json.dumps(value, default=str), ex=ttl)
        logger.debug("cache_set", key=key, ttl=ttl)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)
        logger.debug("cache_delete", key=key)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern using SCAN (avoids KEYS * in production)."""
        cursor: int = 0
        deleted = 0
        while True:
            cursor, keys = await self._client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self._client.delete(*keys)
                deleted += len(keys)
            if cursor == 0:
                break
        logger.debug("cache_delete_pattern", pattern=pattern, deleted=deleted)
        return deleted


async def get_cache() -> AsyncGenerator[RedisCache, None]:
    """FastAPI dependency that yields a RedisCache backed by the shared pool."""
    if _redis_pool is None:
        raise RuntimeError("Redis pool not initialised — call init_redis_pool() at startup")
    yield RedisCache(_redis_pool)
    # Do NOT close — pool is long-lived and shared across all requests
