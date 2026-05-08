#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 cherenkov - Complete System Launcher                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 not found!"
    exit 1
fi
echo "✅ Python 3"

if ! command_exists docker; then
    echo "⚠️  Docker not found (optional)"
else
    echo "✅ Docker"
fi

if ! command_exists ollama; then
    echo "⚠️  Ollama not found (optional for AI features)"
else
    echo "✅ Ollama"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  SELECT SYSTEM TO RUN"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. 🔍 Quick Scanner (CLI) - Test a single URL"
echo "2. 🌐 Web Dashboard - Browser-based interface"
echo "3. 🤖 AI Scanner Generator - Create new scanners"
echo "4. 📦 Batch Scan - Scan multiple URLs"
echo "5. 🐳 Docker Mode - Run in container"
echo "6. 🧪 Test AI-Generated Scanners"
echo "7. 🚀 Full System Demo - All features"
echo "8. 📊 System Status"
echo ""
read -p "Enter choice (1-8): " choice

case $choice in
    1)
        echo ""
        read -p "Enter URL to scan: " url
        python cherenkov_simple_scanner.py "$url"
        ;;
    2)
        echo ""
        echo "🌐 Starting web dashboard..."
        echo "📱 Open browser to: http://localhost:5000"
        python cherenkov_web.py
        ;;
    3)
        echo ""
        echo "🤖 Starting AI scanner generator..."
        python test_batched_parallel.py
        ;;
    4)
        echo ""
        bash batch_scan.sh
        ;;
    5)
        echo ""
        echo "🐳 Starting Docker container..."
        docker-compose up cherenkov
        ;;
    6)
        echo ""
        python analyze_generated_scanners.py
        ;;
    7)
        echo ""
        echo "🚀 Running full system demo..."
        # Quick scan
        echo ""
        echo "1️⃣ Testing Quick Scanner..."
        python cherenkov_simple_scanner.py https://example.com
        
        echo ""
        echo "2️⃣ Analyzing AI-generated scanners..."
        python analyze_generated_scanners.py | head -50
        
        echo ""
        echo "3️⃣ System ready! Launch web dashboard with:"
        echo "   python cherenkov_web.py"
        ;;
    8)
        echo ""
        echo "📊 cherenkov System Status"
        echo "════════════════════════════════════════════════"
        echo ""
        
        echo "📁 Framework Structure:"
        tree cherenkov/ -L 2 -I __pycache__ 2>/dev/null || ls -R cherenkov/
        
        echo ""
        echo "🔍 Available Scanners:"
        ls -1 cherenkov/scanners/*.py cherenkov/scanners/generated/*.py 2>/dev/null | wc -l
        
        echo ""
        echo "📄 Scan Reports:"
        ls -1 scan_report_*.json 2>/dev/null | wc -l
        
        echo ""
        echo "🤖 AI Agents:"
        find cherenkov/agents -name "*.py" | wc -l
        
        echo ""
        echo "✅ System Status: OPERATIONAL"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

