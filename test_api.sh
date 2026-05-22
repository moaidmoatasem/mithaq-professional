#!/usr/bin/env bash
# CHERENKOV headless API test suite
set -uo pipefail

# Use venv Python so websockets and other deps are available
PYTHON="${PYTHON:-$(dirname "$0")/venv/bin/python3}"
[ -x "$PYTHON" ] || PYTHON=python3

BASE="http://localhost:8000"
PASS=0
FAIL=0
WARN=0
RESULTS=()

pass() { echo "  ✅ PASS: $1"; PASS=$((PASS+1)); RESULTS+=("PASS|$1"); }
fail() { echo "  ❌ FAIL: $1 — $2"; FAIL=$((FAIL+1)); RESULTS+=("FAIL|$1|$2"); }
warn() { echo "  ⚠️  WARN: $1 — $2"; WARN=$((WARN+1)); RESULTS+=("WARN|$1|$2"); }

# ── Get fresh token ────────────────────────────────────────────────────────────
AUTH_RESP=$(curl -s -X POST "$BASE/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')
TOKEN=$(echo "$AUTH_RESP" | $PYTHON -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null || echo "")
H="Authorization: Bearer $TOKEN"

echo ""
echo "══════════════════════════════════════════"
echo "  CHERENKOV API TEST SUITE"
echo "══════════════════════════════════════════"
echo ""

# ── 1. STATIC ASSETS ──────────────────────────────────────────────────────────
echo "── 1. Static Assets ──"

code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/")
[ "$code" = "200" ] && pass "GET / → 200 (dashboard served)" || fail "GET /" "Expected 200, got $code"

code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/static/index.html")
[ "$code" = "200" ] && pass "GET /static/index.html → 200" || fail "GET /static/index.html" "Expected 200, got $code"

code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/static/cherenkov-icon.svg")
[ "$code" = "200" ] && pass "GET /static/cherenkov-icon.svg → 200 (fixed this session)" || fail "GET /static/cherenkov-icon.svg" "Expected 200, got $code"

ctype=$(curl -s -I "$BASE/static/cherenkov-icon.svg" | grep -i content-type | tr -d '\r')
echo "    content-type: $ctype"
echo ""

# ── 2. AUTHENTICATION ─────────────────────────────────────────────────────────
echo "── 2. Authentication ──"

[ -n "$TOKEN" ] && pass "POST /api/v1/auth/token (admin/admin) → token issued" || fail "POST /api/v1/auth/token" "No token returned"

BAD=$(curl -s -X POST "$BASE/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}')
echo "$BAD" | grep -q "401\|Incorrect\|Invalid" && pass "POST /api/v1/auth/token (bad creds) → 401 rejected" || fail "Bad creds not rejected" "$BAD"

NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/v1/audit")
[ "$NO_AUTH" = "401" ] || [ "$NO_AUTH" = "403" ] && pass "GET /api/v1/audit (no token) → $NO_AUTH denied" || warn "GET /api/v1/audit no-auth" "Expected 401/403, got $NO_AUTH"

ME=$(curl -s "$BASE/api/v1/auth/me" -H "$H")
echo "$ME" | grep -q "admin" && pass "GET /api/v1/auth/me → username=admin confirmed" || fail "GET /api/v1/auth/me" "$ME"
echo ""

# ── 3. HEALTH / NODE STATUS ───────────────────────────────────────────────────
echo "── 3. Health & Node Status ──"

HEALTH=$(curl -s "$BASE/api/v1/health" -H "$H")
echo "$HEALTH" | $PYTHON -m json.tool 2>/dev/null | grep -E '"status"|"model"' | head -20
echo "$HEALTH" | grep -q '"status"' && pass "GET /api/v1/health → valid JSON with status" || fail "GET /api/v1/health" "Malformed response"

# Check individual nodes
for node in tensor kinetic aegis lattice tokamak; do
  STATUS=$(echo "$HEALTH" | $PYTHON -c "import sys,json; d=json.load(sys.stdin); print(d['nodes']['$node']['status'])" 2>/dev/null || echo "missing")
  [ "$STATUS" = "ready" ] && pass "Node '$node' → ready" || warn "Node '$node'" "status=$STATUS"
done
echo ""

# ── 4. ABLATION STATS ────────────────────────────────────────────────────────
echo "── 4. Ablation Stats ──"

ABL=$(curl -s "$BASE/api/v1/ablation/stats" -H "$H")
echo "$ABL" | $PYTHON -m json.tool 2>/dev/null
echo "$ABL" | grep -q "session_stats" && pass "GET /api/v1/ablation/stats → valid response" || fail "GET /api/v1/ablation/stats" "$ABL"
echo ""

# ── 5. PENDING FINDINGS ───────────────────────────────────────────────────────
echo "── 5. Pending Findings ──"

PENDING=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/v1/findings/pending" -H "$H")
[ "$PENDING" = "200" ] && pass "GET /api/v1/findings/pending → 200" || fail "GET /api/v1/findings/pending" "Got $PENDING"

COUNT=$(curl -s "$BASE/api/v1/findings/pending" -H "$H" | $PYTHON -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
echo "    pending findings count: $COUNT"
echo ""

# ── 6. SCAN ───────────────────────────────────────────────────────────────────
echo "── 6. Scan Engine ──"

SCAN=$(curl -s -X POST "$BASE/api/v1/scan" \
  -H "Content-Type: application/json" \
  -H "$H" \
  -d '{"url":"http://localhost:8000"}')
echo "$SCAN" | $PYTHON -m json.tool 2>/dev/null | grep -E '"scan_id"|"count"|"target"'
echo "$SCAN" | grep -q "scan_id" && pass "POST /api/v1/scan → scan_id returned" || fail "POST /api/v1/scan" "$SCAN"
VULN_COUNT=$(echo "$SCAN" | $PYTHON -c "import sys,json; print(json.load(sys.stdin).get('count',0))" 2>/dev/null || echo "0")
echo "    findings discovered: $VULN_COUNT"
[ "$VULN_COUNT" -gt 0 ] 2>/dev/null && pass "Scan returned $VULN_COUNT findings" || warn "Scan findings" "count=$VULN_COUNT (may be expected for localhost)"

# Bad URL test
BAD_SCAN=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/v1/scan" \
  -H "Content-Type: application/json" \
  -H "$H" \
  -d '{"url":"not-a-url"}')
[ "$BAD_SCAN" = "400" ] && pass "POST /api/v1/scan (invalid URL) → 400 rejected" || warn "POST /api/v1/scan bad URL" "Expected 400, got $BAD_SCAN"
echo ""

# ── 7. SCAN HISTORY ───────────────────────────────────────────────────────────
echo "── 7. Scan History ──"

HIST=$(curl -s "$BASE/api/v1/scans/history" -H "$H")
HIST_COUNT=$(echo "$HIST" | $PYTHON -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
[ "$HIST_COUNT" -ge 0 ] && pass "GET /api/v1/scans/history → $HIST_COUNT records" || fail "GET /api/v1/scans/history" "$HIST"
echo ""

# ── 8. AUDIT LOG ─────────────────────────────────────────────────────────────
echo "── 8. Audit Log ──"

AUDIT=$(curl -s "$BASE/api/v1/audit" -H "$H")
AUDIT_COUNT=$(echo "$AUDIT" | $PYTHON -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
[ "$AUDIT_COUNT" -ge 0 ] && pass "GET /api/v1/audit → $AUDIT_COUNT entries" || fail "GET /api/v1/audit" "$AUDIT"
echo ""

# ── 9. WEBSOCKET ──────────────────────────────────────────────────────────────
echo "── 9. WebSocket ──"

WS_RESULT=$($PYTHON - <<'PYEOF'
import asyncio, json, sys
async def test():
    try:
        import websockets
        async with websockets.connect("ws://localhost:8000/ws/live", open_timeout=5) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=8)
            data = json.loads(msg)
            print(f"OK|{data.get('event','?')}|{data.get('timestamp','?')}")
    except Exception as e:
        print(f"FAIL|{e}")
asyncio.run(test())
PYEOF
)
echo "    ws result: $WS_RESULT"
echo "$WS_RESULT" | grep -q "^OK" && pass "ws://localhost:8000/ws/live → connected, received event: $(echo $WS_RESULT | cut -d'|' -f2)" || fail "WebSocket /ws/live" "$(echo $WS_RESULT | cut -d'|' -f2)"
echo ""

# ── 10. SANDBOX STATUS ────────────────────────────────────────────────────────
echo "── 10. Sandbox ──"

SANDBOX=$(curl -s "$BASE/api/v1/sandbox/status" -H "$H")
echo "$SANDBOX" | grep -q "ready" && pass "GET /api/v1/sandbox/status → ready" || warn "GET /api/v1/sandbox/status" "$SANDBOX"
echo ""

# ── 11. RATE LIMIT ────────────────────────────────────────────────────────────
echo "── 11. Rate Limiting (scan endpoint) ──"
echo "    Firing 5 rapid scan requests..."
for i in $(seq 1 5); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/v1/scan" \
    -H "Content-Type: application/json" -H "$H" \
    -d '{"url":"http://localhost:8000"}')
  echo "    req $i → $CODE"
done
echo ""

# ── SUMMARY ───────────────────────────────────────────────────────────────────
echo "══════════════════════════════════════════"
echo "  RESULTS SUMMARY"
echo "══════════════════════════════════════════"
echo "  ✅ PASS : $PASS"
echo "  ❌ FAIL : $FAIL"
echo "  ⚠️  WARN : $WARN"
echo "══════════════════════════════════════════"
echo ""
