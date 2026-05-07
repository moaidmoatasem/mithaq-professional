#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🔥 TRIPLE THREAT LAUNCH - ALL SYSTEMS GO!                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create logs directory
mkdir -p logs

echo "1️⃣  Starting celebration scans..."
./celebration_scan.sh > logs/celebration_scan.log 2>&1 &
SCAN_PID=$!

echo "2️⃣  Dockerizing everything..."
./dockerize_everything.sh > logs/dockerize.log 2>&1
echo "   ✅ Dockerization complete!"

echo "3️⃣  Launching autonomous roadmap executor..."
echo ""
echo "⚠️  WARNING: This will run continuously!"
echo "   AI agents will work through the entire roadmap."
echo "   Press Ctrl+C to stop at any time."
echo ""
read -p "Start autonomous development? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    python autonomous_roadmap_executor.py
fi

# Wait for scan to complete
wait $SCAN_PID

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ TRIPLE THREAT COMPLETE!                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results:"
echo "  • Scans: Check output/"
echo "  • Docker: Run './docker-manage.sh up'"
echo "  • Autonomous Dev: Check autonomous_development/"
echo ""
