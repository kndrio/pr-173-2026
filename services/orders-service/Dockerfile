# Stage 1: builder — install dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime — lean image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create non-root user (Constitution IV)
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app

# Copy application source
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser alembic/ alembic/
COPY --chown=appuser:appuser app/ app/
COPY --chown=appuser:appuser tests/ tests/
COPY --chown=appuser:appuser scripts/ scripts/

USER appuser

EXPOSE 8002

# Run migrations then start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 1"]
