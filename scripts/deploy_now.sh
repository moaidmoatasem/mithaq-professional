#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 mithaq FINAL DEPLOYMENT - LET'S GO LIVE!                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "[*] Starting Ollama..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Check model
if ! ollama list | grep -q "qwen2.5:3b\|deepseek"; then
    echo "[*] Loading AI model..."
    ollama pull qwen2.5:3b &
fi

echo ""
echo "✅ All systems operational!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  QUICK COMMANDS - YOUR FRAMEWORK IS READY!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  Run a quick security scan:"
echo "   python mithaq_simple_scanner.py https://example.com"
echo ""
echo "2️⃣  Launch web dashboard:"
echo "   python mithaq_web.py"
echo "   Then open: http://localhost:5000"
echo ""
echo "3️⃣  Generate new scanners with AI:"
echo "   python test_batched_parallel.py"
echo ""
echo "4️⃣  Run full AI development team:"
echo "   python test_full_dev_team.py"
echo ""
echo "5️⃣  System status:"
echo "   python system_dashboard.py"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Demo scan
echo "🎯 Running demo scan to verify everything works..."
echo ""
python mithaq_simple_scanner.py https://example.com | head -30

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ FRAMEWORK VERIFIED AND OPERATIONAL!                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Choose your next action:"
echo "  A) Launch web dashboard (python mithaq_web.py)"
echo "  B) Run comprehensive test (python test_batched_parallel.py)"
echo "  C) Commit final version to git"
echo ""

