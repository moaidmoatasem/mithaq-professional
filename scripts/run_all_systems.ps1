# CHERENKOV - Complete System Launcher (Windows Edition)
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║  🚀 CHERENKOV - Complete System Launcher                        ║" -ForegroundColor Blue
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check prerequisites
Write-Host "🔍 Checking prerequisites..."

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python" -ForegroundColor Green

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  Docker not found (optional)" -ForegroundColor Yellow
} else {
    Write-Host "✅ Docker" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════"
Write-Host "  SELECT SYSTEM TO RUN"
Write-Host "═══════════════════════════════════════════════════════════════"
Write-Host ""
Write-Host "1. 🔍 Quick Scanner (CLI) - Test a single URL"
Write-Host "2. 🌐 Web Dashboard - Browser-based interface"
Write-Host "3. 🤖 AI Scanner Generator - Create new scanners"
Write-Host "4. 📦 Batch Scan - Scan multiple URLs"
Write-Host "5. 🐳 Docker Mode - Run in container"
Write-Host "6. 🧪 Test AI-Generated Scanners"
Write-Host "7. 🚀 Full System Demo - All features"
Write-Host "8. 📊 System Status"
Write-Host ""

$choice = Read-Host "Enter choice (1-8)"

switch ($choice) {
    "1" {
        Write-Host ""
        $url = Read-Host "Enter URL to scan"
        python src/cherenkov_cli.py $url
    }
    "2" {
        Write-Host ""
        Write-Host "🌐 Starting web dashboard..." -ForegroundColor Cyan
        Write-Host "📱 Open browser to: http://localhost:5000"
        python src/cherenkov_web.py
    }
    "3" {
        Write-Host ""
        Write-Host "🤖 Starting AI scanner generator..." -ForegroundColor Cyan
        python scripts/test_batched_parallel.py
    }
    "4" {
        Write-Host ""
        Write-Host "📦 Batch scanning is currently optimized for Linux." -ForegroundColor Yellow
        Write-Host "Running sequential batch scan instead..."
        python scripts/batch_scan.py
    }
    "5" {
        Write-Host ""
        Write-Host "🐳 Starting Docker container..." -ForegroundColor Cyan
        docker-compose up cherenkov
    }
    "6" {
        Write-Host ""
        python scripts/analyze_generated_scanners.py
    }
    "7" {
        Write-Host ""
        Write-Host "🚀 Running full system demo..." -ForegroundColor Green
        Write-Host ""
        Write-Host "1️⃣ Testing Quick Scanner..."
        python src/cherenkov_cli.py https://example.com
        
        Write-Host ""
        Write-Host "2️⃣ Analyzing AI-generated scanners..."
        python scripts/analyze_generated_scanners.py | Select-Object -First 50
        
        Write-Host ""
        Write-Host "3️⃣ System ready! Launch web dashboard with:"
        Write-Host "   python src/cherenkov_web.py"
    }
    "8" {
        Write-Host ""
        Write-Host "📊 CHERENKOV System Status" -ForegroundColor Cyan
        Write-Host "════════════════════════════════════════════════"
        Write-Host ""
        
        Write-Host "📁 Framework Structure:"
        Get-ChildItem src/cherenkov -Depth 1
        
        Write-Host ""
        Write-Host "🔍 Available Scanners:"
        (Get-ChildItem src/cherenkov/scanners/*.py -Recurse).Count
        
        Write-Host ""
        Write-Host "✅ System Status: OPERATIONAL" -ForegroundColor Green
    }
    Default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        exit 1
    }
}
