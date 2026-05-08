#!/bin/bash
# Start Web Dashboard

cd "$(dirname "$0")/../src/cherenkov/web"

echo "🌐 Starting cherenkov Web Dashboard..."
echo "📡 Dashboard: http://localhost:8080"
echo ""

python3 -m http.server 8080

