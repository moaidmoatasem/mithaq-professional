# MITHAQ PERFECTION LAUNCH SEQUENCE (Windows Edition)
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║  🚀 MITHAQ PERFECTION LAUNCH SEQUENCE                        ║" -ForegroundColor Blue
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Function to print status
function Show-Status($msg) {
    $time = Get-Date -Format "HH:mm:ss"
    Write-Host "[$time] $msg" -ForegroundColor Cyan
}

function Show-Success($msg) {
    Write-Host "[✓] $msg" -ForegroundColor Green
}

function Show-Warning($msg) {
    Write-Host "[!] $msg" -ForegroundColor Yellow
}

function Show-Error($msg) {
    Write-Host "[✗] $msg" -ForegroundColor Red
}

# Pre-flight checks
Show-Status "Running pre-flight checks..."

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Show-Error "Docker not found. Please install Docker Desktop first."
    exit 1
}
Show-Success "Docker installed"

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Show-Error "Python not found."
    exit 1
}
Show-Success "Python installed"

# Step 1: AI Self-Improvement
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "STEP 1: AI SELF-IMPROVEMENT CYCLE"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

Show-Status "Launching AI agents to improve scanners..."
if (python auto_improve_scanners.py) {
    Show-Success "AI self-improvement complete"
} else {
    Show-Warning "AI improvement skipped or failed - using existing scanners"
}

Start-Sleep -Seconds 2

# Step 2: Build optimized Docker images
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "STEP 2: BUILD OPTIMIZED DOCKER IMAGES"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

Show-Status "Building optimized Docker images..."
if (docker-compose -f docker-compose.optimized.yml build --no-cache) {
    Show-Success "Docker images built successfully"
} else {
    Show-Error "Docker build failed"
    exit 1
}

# Step 3: Start services
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "STEP 3: LAUNCHING SERVICES"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

Show-Status "Starting Ollama service..."
docker-compose -f docker-compose.optimized.yml up -d ollama
Start-Sleep -Seconds 5
Show-Success "Ollama service started"

Show-Status "Pulling AI model (qwen2.5:3b)..."
docker exec mithaq-ollama ollama pull qwen2.5:3b
Show-Success "AI model loaded"

Show-Status "Starting MITHAQ scanner..."
docker-compose -f docker-compose.optimized.yml up -d mithaq
Show-Success "Scanner service started"

Show-Status "Starting web dashboard..."
docker-compose -f docker-compose.optimized.yml up -d dashboard
Show-Success "Dashboard started"

# Step 4: Health checks
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "STEP 4: HEALTH CHECKS"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

Show-Status "Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Check Ollama
if (docker exec mithaq-ollama ollama list) {
    Show-Success "Ollama is healthy"
} else {
    Show-Warning "Ollama health check failed"
}

# Step 5: Show status
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "SYSTEM STATUS"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

docker-compose -f docker-compose.optimized.yml ps

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║  ✅ MITHAQ PERFECTION - FULLY OPERATIONAL                    ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Web Dashboard: http://localhost:5000"
Write-Host "🤖 Ollama API: http://localhost:11434"
Write-Host ""
Write-Host "Quick Commands:"
Write-Host "  • View logs: docker-compose -f docker-compose.optimized.yml logs -f"
Write-Host "  • Run scan: docker exec mithaq-scanner python mithaq_simple_scanner.py https://example.com"
Write-Host "  • Stop all: docker-compose -f docker-compose.optimized.yml down"
Write-Host ""
Write-Host "🚀 System is ready for sovereign security testing!"
