#!/usr/bin/env bash
# Show swarm status: running/stopped, queue stats, recent log lines.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

PIDFILE="$SCRIPT_DIR/logs/swarm.pid"
LOGFILE="$SCRIPT_DIR/logs/swarm.log"
ISSUE_QUEUE="manifests/issue_queue.yaml"
CWE_QUEUE="manifests/cwe_queue.yaml"

echo "═══════════════════════════════════════════"
echo "  CHERENKOV Swarm Status"
echo "═══════════════════════════════════════════"

# Process
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "  Process : RUNNING (PID $(cat "$PIDFILE"))"
else
    echo "  Process : STOPPED"
fi

# Issue queue
if [ -f "$ISSUE_QUEUE" ]; then
    echo ""
    echo "  GitHub Issue Queue ($ISSUE_QUEUE):"
    python3 -c "
import yaml, sys
data = yaml.safe_load(open('$ISSUE_QUEUE')) or {}
issues = data.get('issues', [])
by_status = {}
for i in issues:
    s = i.get('status','?')
    by_status[s] = by_status.get(s,0) + 1
for s, n in sorted(by_status.items()):
    print(f'    {s:15s}: {n}')
if not issues:
    print('    (empty)')
" 2>/dev/null || echo "    (parse error)"
fi

# CWE queue
if [ -f "$CWE_QUEUE" ]; then
    echo ""
    echo "  CWE Queue ($CWE_QUEUE):"
    python3 -c "
import yaml
data = yaml.safe_load(open('$CWE_QUEUE')) or {}
queue = data.get('queue', [])
by_status = {}
for i in queue:
    s = i.get('status','pending')
    by_status[s] = by_status.get(s,0) + 1
for s, n in sorted(by_status.items()):
    print(f'    {s:15s}: {n}')
if not queue:
    print('    (empty)')
" 2>/dev/null || echo "    (parse error)"
fi

# Candidates
CAND=$(ls candidates/generated_scanners/*.py 2>/dev/null | wc -l)
echo ""
echo "  Candidates : $CAND file(s) in candidates/generated_scanners/"

# Recent logs
if [ -f "$LOGFILE" ]; then
    echo ""
    echo "  Last 10 log lines:"
    tail -10 "$LOGFILE" | sed 's/^/    /'
fi

echo "═══════════════════════════════════════════"
