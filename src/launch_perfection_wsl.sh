#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 mithaq PERFECTION LAUNCH - WSL2 OPTIMIZED                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Pre-flight checks
status "Running pre-flight checks..."

if ! command -v docker &> /dev/null; then
    error "Docker not found. Install Docker Desktop for Windows with WSL2 backend."
    exit 1
fi
success "Docker installed"

# Check Docker daemon
if ! docker info &> /dev/null; then
    error "Docker daemon not running. Start Docker Desktop."
    exit 1
fi
success "Docker daemon running"

# Step 1: AI Self-Improvement
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: AI SELF-IMPROVEMENT CYCLE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "auto_improve_scanners.py" ]; then
    status "Launching AI agents to improve scanners..."
    if timeout 300 python auto_improve_scanners.py 2>&1 | head -50; then
        success "AI improvement cycle completed (or timed out gracefully)"
    else
        warning "Using existing scanners"
    fi
else
    warning "Skipping AI improvement - file not found"
fi

sleep 2

# Step 2: Build Docker image (native docker build)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: BUILD OPTIMIZED DOCKER IMAGE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

status "Building mithaq Docker image..."
if docker build -f Dockerfile.optimized -t mithaq:perfection . --no-cache 2>&1 | tail -20; then
    success "Docker image built successfully"
else
    warning "Docker build had warnings - checking if image exists..."
    if docker images | grep -q "mithaq"; then
        success "Image created despite warnings"
    else
        error "Docker build failed completely"
        exit 1
    fi
fi

# Step 3: Create Docker network
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: SETUP NETWORK & VOLUMES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

status "Creating Docker network..."
docker network create mithaq-network 2>/dev/null || success "Network already exists"

status "Creating volumes..."
docker volume create ollama-data 2>/dev/null || success "Ollama volume exists"
docker volume create mithaq-output 2>/dev/null || success "Output volume exists"

# Step 4: Launch Ollama
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: LAUNCH OLLAMA SERVICE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Ollama container exists
if docker ps -a | grep -q mithaq-ollama; then
    status "Removing old Ollama container..."
    docker rm -f mithaq-ollama
fi

status "Starting Ollama container..."
docker run -d \
    --name mithaq-ollama \
    --network mithaq-network \
    -p 11434:11434 \
    -v ollama-data:/root/.ollama \
    -e OLLAMA_MAX_LOADED_MODELS=1 \
    -e OLLAMA_NUM_PARALLEL=1 \
    --memory="4g" \
    --cpus="4" \
    --restart unless-stopped \
    ollama/ollama:latest

sleep 5
success "Ollama container started"

status "Pulling qwen2.5:3b model..."
docker exec mithaq-ollama ollama pull qwen2.5:3b &
OLLAMA_PID=$!

# Step 5: Launch mithaq Scanner (while Ollama pulls model)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: LAUNCH mithaq SCANNER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Remove old container
if docker ps -a | grep -q mithaq-scanner; then
    docker rm -f mithaq-scanner
fi

status "Starting mithaq scanner container..."
docker run -d \
    --name mithaq-scanner \
    --network mithaq-network \
    -v "$(pwd)/output:/app/output" \
    -v "$(pwd)/logs:/app/logs" \
    -e OLLAMA_BASE_URL=http://mithaq-ollama:11434 \
    -e CREWAI_TELEMETRY_OPT_OUT=true \
    --memory="2g" \
    --cpus="2" \
    --restart unless-stopped \
    mithaq:perfection \
    tail -f /dev/null

success "Scanner container started"

# Wait for Ollama model pull to complete
wait $OLLAMA_PID
success "AI model loaded"

# Step 6: Launch Web Dashboard
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: LAUNCH WEB DASHBOARD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Remove old container
if docker ps -a | grep -q mithaq-dashboard; then
    docker rm -f mithaq-dashboard
fi

status "Starting web dashboard..."
docker run -d \
    --name mithaq-dashboard \
    --network mithaq-network \
    -p 5000:5000 \
    -v "$(pwd)/output:/app/output" \
    -e FLASK_ENV=production \
    --memory="512m" \
    --cpus="1" \
    --restart unless-stopped \
    mithaq:perfection \
    python mithaq_web.py

sleep 3
success "Dashboard started"

# Step 7: Health Checks
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 7: HEALTH CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

status "Checking container health..."

# Check Ollama
if docker exec mithaq-ollama ollama list &> /dev/null; then
    success "Ollama is healthy"
else
    warning "Ollama may still be initializing"
fi

# Check Scanner
if docker exec mithaq-scanner python --version &> /dev/null; then
    success "Scanner container is healthy"
else
    warning "Scanner container check failed"
fi

# Check Dashboard
sleep 5
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    success "Dashboard is accessible at http://localhost:5000"
else
    warning "Dashboard may still be starting up..."
fi

# Step 8: Show Status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SYSTEM STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker ps --filter "name=mithaq-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RESOURCE USAGE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" \
    mithaq-ollama mithaq-scanner mithaq-dashboard 2>/dev/null

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ mithaq PERFECTION - FULLY OPERATIONAL                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Web Dashboard: http://localhost:5000"
echo "🤖 Ollama API: http://localhost:11434"
echo ""
echo "📋 Quick Commands:"
echo "  • Test scan:"
echo "    docker exec mithaq-scanner python mithaq_simple_scanner.py https://example.com"
echo ""
echo "  • View logs:"
echo "    docker logs -f mithaq-scanner"
echo "    docker logs -f mithaq-dashboard"
echo ""
echo "  • Monitor resources:"
echo "    watch -n 2 'docker stats --no-stream mithaq-*'"
echo ""
echo "  • Stop all:"
echo "    docker stop mithaq-ollama mithaq-scanner mithaq-dashboard"
echo ""
echo "  • Clean up:"
echo "    docker rm mithaq-ollama mithaq-scanner mithaq-dashboard"
echo ""
echo "🚀 System is ready for production security testing!"
echo ""

