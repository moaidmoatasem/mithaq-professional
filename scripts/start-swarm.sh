#!/usr/bin/env bash
# Start the CHERENKOV SwarmOrchestrator in the background.
# Logs to logs/swarm.log. Safe to re-run — checks if already running.

set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

PIDFILE="$SCRIPT_DIR/logs/swarm.pid"
LOGFILE="$SCRIPT_DIR/logs/swarm.log"

mkdir -p logs candidates/generated_scanners

# Check if already running
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Swarm already running (PID $(cat "$PIDFILE")). Log: $LOGFILE"
    exit 0
fi

nohup bash -c "
    export PATH=\"$HOME/.local/bin:\$PATH\"
    cd \"$SCRIPT_DIR\"
    exec PYTHONPATH=packages python3 packages/cherenkov/dev_crew/swarm_orchestrator.py
" >> "$LOGFILE" 2>&1 &

echo $! > "$PIDFILE"
echo "Swarm started (PID $!). Tailing logs..."
sleep 2
tail -f "$LOGFILE"
