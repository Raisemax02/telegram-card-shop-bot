# ============================================================
# STAGE 1: Builder — Install all dependencies
# ============================================================
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies for compiling native packages (e.g. cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy project metadata and create minimal package for pip
COPY pyproject.toml ./
RUN mkdir -p app && touch app/__init__.py

# Install project and its dependencies via pip + setuptools
RUN pip install --no-cache-dir .

# ============================================================
# STAGE 2: Runtime — Lightweight final image
# ============================================================
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash botuser

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY app/ ./app/

# Create data and logs directories (for Docker volumes)
RUN mkdir -p /app/data /app/logs && chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Health check: verify bot process is alive and logging recently
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys,time;from pathlib import Path;log=Path('/app/logs/bot.log');sys.exit(0 if log.exists() and time.time()-log.stat().st_mtime<120 else 1)" || exit 1

# Start the bot
CMD ["python", "-m", "app.main"]