import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import fakeredis.aioredis as fakeredis

import app.core.cache as cache_module
from app.core.cache import RedisCache, get_cache
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():  # type: ignore[override]
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:  # type: ignore[no-untyped-def]
    # Bind to an open connection and begin a transaction; rollback at teardown
    # so that even committed writes from endpoint code are rolled back.
    async with test_engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(conn, expire_on_commit=False)
        yield session
        await conn.rollback()


@pytest_asyncio.fixture
async def fake_redis_client() -> AsyncGenerator[fakeredis.FakeRedis, None]:
    # Function-scoped so each test starts with a clean Redis state (no cache pollution).
    redis = fakeredis.FakeRedis(decode_responses=True)
    cache_module._redis_pool = redis  # type: ignore[assignment]
    yield redis
    await redis.aclose()
    cache_module._redis_pool = None


def _make_token(user_id: uuid.UUID | None = None) -> str:
    payload = {
        "sub": str(user_id or uuid.uuid4()),
        "email": "test@example.com",
        "role": "operator",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


@pytest_asyncio.fixture
async def unauth_client(
    db_session: AsyncSession,
    fake_redis_client: fakeredis.FakeRedis,
) -> AsyncGenerator[AsyncClient, None]:
    """Client without Authorization header — for testing 401 responses."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def override_get_cache() -> AsyncGenerator[RedisCache, None]:
        yield RedisCache(fake_redis_client)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache] = override_get_cache

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
    fake_redis_client: fakeredis.FakeRedis,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def override_get_cache() -> AsyncGenerator[RedisCache, None]:
        yield RedisCache(fake_redis_client)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache] = override_get_cache

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {_make_token()}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
