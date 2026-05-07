#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🐳 DOCKERIZE EVERYTHING - PRODUCTION CONTAINERS            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create optimized Dockerfile
cat > Dockerfile << 'DOCKER'
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
LABEL description="mithaq - AI-Powered Security Framework"
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
COPY mithaq/ ./mithaq/
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
CMD ["python", "mithaq_simple_scanner.py", "--help"]
DOCKER

echo "✅ Dockerfile created"

# Create docker-compose for full stack
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  # Ollama AI Service
  ollama:
    image: ollama/ollama:latest
    container_name: mithaq-ollama
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_MAX_LOADED_MODELS=2
      - OLLAMA_NUM_PARALLEL=2
    networks:
      - mithaq-net
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 6G
        reservations:
          memory: 2G
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 30s
      timeout: 10s
      retries: 3

  # mithaq Scanner Service
  scanner:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mithaq-scanner
    depends_on:
      - ollama
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - CREWAI_TELEMETRY_OPT_OUT=true
    networks:
      - mithaq-net
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
    restart: unless-stopped
    command: tail -f /dev/null

  # Web Dashboard
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mithaq-dashboard
    depends_on:
      - scanner
      - ollama
    ports:
      - "5000:5000"
    volumes:
      - ./output:/app/output
    environment:
      - FLASK_ENV=production
      - OLLAMA_BASE_URL=http://ollama:11434
    networks:
      - mithaq-net
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
    restart: unless-stopped
    command: python mithaq_web.py

  # Redis Cache (for scan results)
  redis:
    image: redis:7-alpine
    container_name: mithaq-redis
    volumes:
      - redis-data:/data
    networks:
      - mithaq-net
    deploy:
      resources:
        limits:
          memory: 256M
    restart: unless-stopped
    command: redis-server --maxmemory 200mb --maxmemory-policy allkeys-lru

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: mithaq-nginx
    depends_on:
      - dashboard
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - mithaq-net
    restart: unless-stopped

networks:
  mithaq-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  ollama-data:
    driver: local
  redis-data:
    driver: local
COMPOSE

echo "✅ docker-compose.yml created"

# Create nginx config
cat > nginx.conf << 'NGINX'
events {
    worker_connections 1024;
}

http {
    upstream dashboard {
        server dashboard:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /api {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
        }
    }
}
NGINX

echo "✅ nginx.conf created"

# Create .dockerignore
cat > .dockerignore << 'IGNORE'
**/__pycache__
**/*.pyc
**/*.pyo
**/*.pyd
.Python
*.so
*.egg
*.egg-info
dist/
build/
.git/
.github/
.vscode/
.idea/
*.md
!README.md
tests/
output/
logs/
*.json
*.log
.env
.venv/
venv/
__pycache__/
IGNORE

echo "✅ .dockerignore created"

# Create docker management scripts
cat > docker-manage.sh << 'MANAGE'
#!/bin/bash

case "$1" in
    build)
        echo "🔨 Building Docker images..."
        docker compose build --no-cache
        ;;
    up)
        echo "🚀 Starting all services..."
        docker compose up -d
        ;;
    down)
        echo "🛑 Stopping all services..."
        docker compose down
        ;;
    restart)
        echo "🔄 Restarting services..."
        docker compose restart
        ;;
    logs)
        docker compose logs -f
        ;;
    status)
        echo "📊 Service Status:"
        docker compose ps
        echo ""
        echo "💾 Resource Usage:"
        docker stats --no-stream
        ;;
    clean)
        echo "🧹 Cleaning up..."
        docker compose down -v
        docker system prune -f
        ;;
    *)
        echo "mithaq Docker Manager"
        echo ""
        echo "Usage: $0 {build|up|down|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  build   - Build all images"
        echo "  up      - Start all services"
        echo "  down    - Stop all services"
        echo "  restart - Restart services"
        echo "  logs    - View logs"
        echo "  status  - Show status and resources"
        echo "  clean   - Remove all containers and volumes"
        ;;
esac
MANAGE

chmod +x docker-manage.sh

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ DOCKERIZATION COMPLETE!                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Files created:"
echo "  • Dockerfile (multi-stage, optimized)"
echo "  • docker-compose.yml (full stack)"
echo "  • nginx.conf (reverse proxy)"
echo "  • .dockerignore (build optimization)"
echo "  • docker-manage.sh (management script)"
echo ""
echo "🚀 Quick Start:"
echo "  ./docker-manage.sh build  # Build images"
echo "  ./docker-manage.sh up     # Start services"
echo "  ./docker-manage.sh status # Check status"
echo ""

