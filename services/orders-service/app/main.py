import uuid

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

import redis.asyncio as aioredis

from app.core.cache import close_redis_pool, init_redis_pool
from app.core.config import settings
from app.core.database import engine
from app.core.logging import configure_logging
from app.routes.orders import router as orders_router

configure_logging()

logger = structlog.get_logger()

app = FastAPI(
    title="Orders Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: object) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )
    response: Response = await call_next(request)  # type: ignore[operator]
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Check database and Redis connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        logger.exception("health_check_db_failed")
        db_status = "unavailable"

    from app.core.cache import _redis_pool

    redis_status = "unavailable"
    try:
        if _redis_pool is not None:
            await _redis_pool.ping()
            redis_status = "connected"
    except Exception:
        logger.exception("health_check_redis_failed")

    overall = "healthy" if db_status == "connected" and redis_status == "connected" else "degraded"
    return {
        "status": overall,
        "service": "orders-service",
        "database": db_status,
        "redis": redis_status,
    }


@app.get("/ready", tags=["ops"])
async def ready() -> dict[str, str]:
    """Readiness probe — returns 200 when the service is ready to accept traffic."""
    return {"status": "ready", "service": "orders-service"}


app.include_router(orders_router)


@app.on_event("startup")
async def startup_event() -> None:
    await init_redis_pool()
    logger.info("orders_service_started", env=settings.env)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_redis_pool()
