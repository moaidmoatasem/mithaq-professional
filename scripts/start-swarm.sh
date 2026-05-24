#!/usr/bin/env bash
# Start the CHERENKOV SwarmOrchestrator in the background.
# Logs to logs/swarm.log. Safe to re-run — checks if already running.

set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

PIDFILE="$SCRIPT_DIR/logs/swarm.pid"
LOGFILE="$SCRIPT_DIR/logs/swarm.log"

mkdir -p logs candidates/generated_scanners manifests

# SWARM_MODE=cwe  → legacy CWE-only SwarmOrchestrator
# SWARM_MODE=issues (default) → AutonomousIssueSwarm (GitHub issues + roadmap)
SWARM_MODE="${SWARM_MODE:-issues}"

if [ "$SWARM_MODE" = "cwe" ]; then
    ENTRYPOINT="packages/cherenkov/dev_crew/swarm_orchestrator.py"
    SWARM_LABEL="CWE Swarm"
else
    ENTRYPOINT="packages/cherenkov/dev_crew/autonomous_issue_swarm.py"
    SWARM_LABEL="Autonomous Issue Swarm"
fi

# Check if already running
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "$SWARM_LABEL already running (PID $(cat "$PIDFILE")). Log: $LOGFILE"
    exit 0
fi

nohup bash -c "
    export PATH=\"$HOME/.local/bin:\$PATH\"
    export PYTHONPATH=\"$SCRIPT_DIR/packages\"
    export SWARM_BATCH_SIZE=\"${SWARM_BATCH_SIZE:-3}\"
    export SWARM_POLL_INTERVAL=\"${SWARM_POLL_INTERVAL:-300}\"
    export SWARM_REPO=\"${SWARM_REPO:-}\"
    cd \"$SCRIPT_DIR\"
    python3 $ENTRYPOINT \${SWARM_REPO}
" >> "$LOGFILE" 2>&1 &

echo $! > "$PIDFILE"
echo "$SWARM_LABEL started (PID $!). Tailing logs..."
sleep 2
tail -f "$LOGFILE"