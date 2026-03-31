import uuid

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.database import engine
from app.core.logging import configure_logging

configure_logging()

logger = structlog.get_logger()

app = FastAPI(
    title="Auth Service",
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


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        logger.exception("health_check_db_failed")
        db_status = "unavailable"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "auth-service",
        "database": db_status,
    }


@app.get("/ready", tags=["health"])
async def ready() -> dict[str, str]:
    """Readiness probe — returns 200 when the service is ready to accept traffic."""
    return {"status": "ready", "service": "auth-service"}


app.include_router(v1_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("auth_service_started", env=settings.env)
