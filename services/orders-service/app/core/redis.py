from collections.abc import AsyncGenerator

import redis.asyncio as aioredis

from app.core.config import settings


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:  # type: ignore[type-arg]
    """Dependency that provides an async Redis client."""
    client: aioredis.Redis = aioredis.from_url(  # type: ignore[type-arg]
        settings.redis_url,
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()
