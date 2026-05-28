#!/bin/bash
# start_cherenkov.sh — One command boots the entire CHERENKOV stack.
# Usage: ./scripts/start_cherenkov.sh
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[\xe2\x9c\x93]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
fail()  { echo -e "${RED}[\xe2\x9c\x97]${NC} $1"; }

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

export CHERENKOV_JWT_SECRET="${CHERENKOV_JWT_SECRET:-$(python3 -c "import secrets; print(secrets.token_hex(32))")}"

cleanup() {
  info "Shutting down services..."
  pkill -f "uvicorn.*cherenkov" 2>/dev/null || true
  pkill -f "litellm" 2>/dev/null || true
}

# ── 1. Kill stale processes ──────────────────────────────────────────
info "Killing stale uvicorn/litellm processes..."
cleanup
sleep 1
ok "Stale processes cleaned"

# ── 2. Start Docker-backed services ──────────────────────────────────
COMPOSE_FILES="-f deploy/docker-compose.yml"
if [ -f "deploy/dvwa-compose.yml" ]; then
  COMPOSE_FILES="$COMPOSE_FILES -f deploy/dvwa-compose.yml"
fi

info "Starting Docker services (Qdrant, Ollama)..."
# shellcheck disable=SC2086
docker compose $COMPOSE_FILES up -d qdrant ollama 2>/dev/null || warn "Docker not available — run services manually"
if echo "$COMPOSE_FILES" | grep -q dvwa; then
  # shellcheck disable=SC2086
  docker compose $COMPOSE_FILES up -d dvwa 2>/dev/null || warn "DVWA start skipped (optional)"
fi

# ── 3. Start LiteLLM (if config exists) ──────────────────────────────
LITELLM_CONFIG="${LITELLM_CONFIG:-$HOME/litellm-config.yaml}"
if [ -f "$LITELLM_CONFIG" ]; then
  info "Starting LiteLLM proxy..."
  nohup litellm --config "$LITELLM_CONFIG" --port 4000 > /tmp/litellm.log 2>&1 &
  LITELLM_PID=$!
  disown "$LITELLM_PID" 2>/dev/null
  ok "LiteLLM starting (PID $LITELLM_PID)"
else
  warn "LiteLLM config not found at $LITELLM_CONFIG — skipping"
fi

# ── 4. Start API server ──────────────────────────────────────────────
info "Starting CHERENKOV API server..."
PYTHONPATH="${REPO_DIR}/packages:${PYTHONPATH:-}" nohup uvicorn cherenkov.api.main:app \
  --host 0.0.0.0 --port 8000 > /tmp/cherenkov-api.log 2>&1 &
API_PID=$!
disown "$API_PID" 2>/dev/null
ok "API server starting (PID $API_PID)"

# ── 5. Health checks ─────────────────────────────────────────────────
echo ""
info "Waiting for services to become available..."
sleep 3

check_service() {
  local name="$1" url="$2" max="$3" optional="${4:-}"
  for _ in $(seq 1 "$max"); do
    if curl -sf "$url" >/dev/null 2>&1; then
      ok "$name is healthy"
      return 0
    fi
    sleep 1
  done
  if [ "$optional" = "optional" ]; then
    warn "$name health check failed (optional service)"
    return 0
  fi
  fail "$name health check failed"
  return 1
}

check_service "Qdrant"    "http://localhost:6333/healthz" 15
check_service "Ollama"    "http://localhost:11434/api/tags" 30
check_service "API"       "http://localhost:8000/docs" 15
check_service "DVWA"      "http://localhost:80" 10 "optional"

if [ -n "${LITELLM_PID:-}" ] && kill -0 "$LITELLM_PID" 2>/dev/null; then
  check_service "LiteLLM" "http://localhost:4000/health" 15
fi

# ── 6. JWT smoke test ────────────────────────────────────────────────
echo ""
info "JWT smoke test (admin/admin)..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

if [ -n "$TOKEN" ]; then
  ok "JWT smoke test passed (token obtained)"
else
  warn "JWT smoke test failed — API may need a moment"
fi

# ── 7. Register c2 alias idempotently ────────────────────────────────
ALIAS_LINE="alias c2='cd $REPO_DIR && python -m cherenkov.cli'"
if ! grep -qxF "$ALIAS_LINE" "$HOME/.bashrc" 2>/dev/null; then
  echo "" >> "$HOME/.bashrc"
  echo "$ALIAS_LINE" >> "$HOME/.bashrc"
  ok "c2 alias added to ~/.bashrc"
else
  ok "c2 alias already present in ~/.bashrc"
fi

# ── 8. Summary ───────────────────────────────────────────────────────
echo ""
echo "+==============================================================+"
echo "|  CHERENKOV stack is ready                                     |"
echo "+==============================================================+"
echo ""
echo "  API       -> http://localhost:8000"
echo "  Docs      -> http://localhost:8000/docs"
echo "  Qdrant    -> http://localhost:6333"
echo "  Ollama    -> http://localhost:11434"
echo "  LiteLLM   -> http://localhost:4000"
echo "  DVWA      -> http://localhost:80"
echo ""
echo "  c2 alias registered - run: c2 scan --help"
echo ""
echo "  Quick commands:"
echo "    c2 scan http://localhost/dvwa"
echo "    docker compose -f deploy/docker-compose.yml logs -f"
echo "    $0  # re-run (idempotent)"
echo ""
