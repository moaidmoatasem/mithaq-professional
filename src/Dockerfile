# Multi-stage build for minimal size
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --user --no-cache-dir --compile -r requirements.txt

# Production image
FROM python:3.11-slim

LABEL maintainer="Moaid EL-Moatasem Bellah"
LABEL description="cherenkov - AI-Powered Security Framework"
LABEL version="1.0.0"

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy application
COPY cherenkov/ ./cherenkov/
COPY *.py ./

# Create necessary directories
RUN mkdir -p output logs /app/.cache

# Set environment
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    MALLOC_TRIM_THRESHOLD_=100000 \
    CREWAI_TELEMETRY_OPT_OUT=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "cherenkov_simple_scanner.py", "--help"]

