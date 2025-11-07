# Python API Dockerfile - Multi-stage build for optimization

# Stage 1: Builder - Install dependencies
FROM python:3.9-slim AS builder

WORKDIR /install

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to /install directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime - Copy only what's needed
FROM python:3.9-slim

WORKDIR /app

# Install only runtime dependencies (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code only (no tests, docs, etc.)
COPY app.py .
COPY config/ ./config/
COPY services/ ./services/
COPY utils/ ./utils/
COPY download_model.py .

# Download BERT model
RUN python download_model.py || echo "Warning: Model download failed, will retry at runtime"

# Create non-root user
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start application with Gunicorn (production-ready WSGI server)
# Workers: 4 (2 x CPU cores recommended for CPU-bound ML tasks)
# Timeout: 120s (ML processing can take time)
# Log to stdout/stderr for Docker logging
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--worker-class", "sync", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]
