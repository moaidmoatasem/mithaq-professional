#!/bin/bash
set -euo pipefail

# Make sure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Starting CHERENKOV orchestrator..."

# Register c2 alias idempotently
if ! grep -q "alias c2='cherenkov'" ~/.bashrc; then
  echo "alias c2='cherenkov'" >> ~/.bashrc
  echo "Registered c2 alias in ~/.bashrc"
fi

# Kill stale processes
echo "Killing stale processes..."
pkill -f uvicorn || true
pkill -f litellm || true

# Start Docker dependencies
echo "Starting Docker dependencies..."
docker run -d --name qdrant --restart unless-stopped -p 6333:6333 qdrant/qdrant 2>/dev/null || docker start qdrant || sudo docker start qdrant || true
docker run -d --name dvwa --restart unless-stopped -p 80:80 ghcr.io/digininja/dvwa:latest 2>/dev/null || docker start dvwa || sudo docker start dvwa || true

# Start Ollama
echo "Starting Ollama..."
if ! pgrep -f "ollama serve" > /dev/null; then
  ollama serve > /dev/null 2>&1 &
fi

# Start LiteLLM proxy
echo "Starting LiteLLM proxy..."
if [ -f ~/litellm-config.yaml ]; then
  litellm --config ~/litellm-config.yaml > /dev/null 2>&1 &
else
  echo "Warning: ~/litellm-config.yaml not found (LiteLLM will not start properly unless it creates it)."
  # Wait, litellm requires the config. We can just try to run litellm --config ~/litellm-config.yaml
  litellm --config ~/litellm-config.yaml > /dev/null 2>&1 &
fi

# Start API server
echo "Starting API server..."
PYTHONPATH="$(pwd)/packages"
export PYTHONPATH
export CHERENKOV_JWT_SECRET="${CHERENKOV_JWT_SECRET:-secret}"
uvicorn cherenkov.api.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

echo "Waiting for services to initialize..."
sleep 10

echo "--- Health ---"
curl -sf http://localhost:6333/healthz > /dev/null && echo " LATTICE (Qdrant)  OK ✓" || echo " LATTICE (Qdrant)  FAIL ✗"
curl -sf http://localhost:80 > /dev/null && echo " DVWA              OK ✓" || echo " DVWA              FAIL ✗"
curl -sf http://localhost:11434/api/tags > /dev/null && echo " Ollama            OK ✓" || echo " Ollama            FAIL ✗"
curl -sf http://localhost:4000/health > /dev/null && echo " LiteLLM           OK ✓" || echo " LiteLLM           FAIL ✗"
curl -sf http://localhost:8000/docs > /dev/null && echo " API Server        OK ✓" || echo " API Server        FAIL ✗"

echo "Running JWT Smoke Test..."
JWT_RESPONSE=$(curl -sf -X POST -H "Content-Type: application/json" http://localhost:8000/v1/auth/token -d '{"username":"admin","password":"password"}' || true)
if echo "$JWT_RESPONSE" | grep -q "token"; then
  echo " JWT Smoke Test    OK ✓"
else
  # Trying admin/admin as well in case the password is admin
  JWT_RESPONSE_2=$(curl -sf -X POST -H "Content-Type: application/json" http://localhost:8000/v1/auth/token -d '{"username":"admin","password":"admin"}' || true)
  if echo "$JWT_RESPONSE_2" | grep -q "token"; then
    echo " JWT Smoke Test    OK ✓"
  else
    echo " JWT Smoke Test    FAIL ✗"
  fi
fi

echo "Startup complete. Exiting successfully."
