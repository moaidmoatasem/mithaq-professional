#!/bin/bash
# Start cherenkov REST API Server

cd "$(dirname "$0")/.."

echo "🚀 Starting cherenkov REST API Server..."
echo "📡 API will be available at: http://localhost:8000"
echo "📖 Documentation: http://localhost:8000/docs"
echo ""

PYTHONPATH=src:. uvicorn src.cherenkov.api.main:app --reload --host 0.0.0.0 --port 8000

