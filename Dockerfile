# Multi-stage Dockerfile for FastAPI + static frontend
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement files
COPY ecommerce/backend/requirements.txt ./

# Install python deps
RUN pip install --upgrade pip && \
    pip install --no-warn-script-location -r requirements.txt

# Copy app code
COPY . .

# Expose the port (Render/other providers often set PORT env)
ENV PORT=8000

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Start the server with uvicorn
CMD ["python", "-m", "uvicorn", "ecommerce.backend.app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
