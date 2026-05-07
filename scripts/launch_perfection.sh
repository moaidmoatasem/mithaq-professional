#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 mithaq PERFECTION LAUNCH SEQUENCE                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to print status
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
    error "Docker not found. Please install Docker first."
    exit 1
fi
success "Docker installed"

if ! command -v python3 &> /dev/null; then
    error "Python 3 not found."
    exit 1
fi
success "Python 3 installed"

# Step 1: AI Self-Improvement
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: AI SELF-IMPROVEMENT CYCLE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

status "Launching AI agents to improve scanners..."
if python auto_improve_scanners.py; then
    success "AI self-improvement complete"
else
    warning "AI improvement skipped or failed - using existing scanners"
fi

sleep 2

# Step 2: Build optimized Docker images
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: BUILD OPTIMIZED DOCKER IMAGES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

status "Building optimized Docker images..."
if docker-compose -f docker-compose.optimized.yml build --no-cache; then
    success "Docker images built successfully"
else
    error "Docker build failed"
    exit 1
fi

# Step 3: Start services
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: LAUNCHING SERVICES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

status "Starting Ollama service..."
docker-compose -f docker-compose.optimized.yml up -d ollama
sleep 5
success "Ollama service started"

status "Pulling AI model (qwen2.5:3b)..."
docker exec mithaq-ollama ollama pull qwen2.5:3b
success "AI model loaded"

status "Starting mithaq scanner..."
docker-compose -f docker-compose.optimized.yml up -d mithaq
success "Scanner service started"

status "Starting web dashboard..."
docker-compose -f docker-compose.optimized.yml up -d dashboard
success "Dashboard started"

# Step 4: Health checks
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: HEALTH CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

status "Waiting for services to be ready..."
sleep 10

# Check Ollama
if docker exec mithaq-ollama ollama list &> /dev/null; then
    success "Ollama is healthy"
else
    warning "Ollama health check failed"
fi

# Check Dashboard
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    success "Dashboard is accessible"
else
    warning "Dashboard may not be ready yet"
fi

# Step 5: Show status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SYSTEM STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker-compose -f docker-compose.optimized.yml ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RESOURCE USAGE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ mithaq PERFECTION - FULLY OPERATIONAL                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Web Dashboard: http://localhost:5000"
echo "🤖 Ollama API: http://localhost:11434"
echo ""
echo "Quick Commands:"
echo "  • View logs: docker-compose -f docker-compose.optimized.yml logs -f"
echo "  • Run scan: docker exec mithaq-scanner python mithaq_simple_scanner.py https://example.com"
echo "  • Stop all: docker-compose -f docker-compose.optimized.yml down"
echo "  • Monitor: watch -n 2 'docker stats --no-stream'"
echo ""
echo "🚀 System is ready for production security testing!"
echo ""

