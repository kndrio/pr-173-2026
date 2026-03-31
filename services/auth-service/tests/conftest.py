import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

# Use SQLite for tests (no PostgreSQL needed)
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
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register a user, log in, and return Authorization headers."""
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Me User", "email": "me@example.com", "password": "securepass123"},
    )
    assert register_resp.status_code == 201, register_resp.text
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "securepass123"},
    )
    assert login_resp.status_code == 200, login_resp.text
    return {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
