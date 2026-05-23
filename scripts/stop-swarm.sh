#!/usr/bin/env bash
# Gracefully stop the running swarm process.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="$SCRIPT_DIR/logs/swarm.pid"

if [ ! -f "$PIDFILE" ]; then
    echo "No swarm PID file found. Nothing to stop."
    exit 0
fi

PID=$(cat "$PIDFILE")
if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping swarm (PID $PID)..."
    kill "$PID"
    sleep 2
    if kill -0 "$PID" 2>/dev/null; then
        kill -9 "$PID"
        echo "Force-killed."
    else
        echo "Swarm stopped."
    fi
else
    echo "Swarm (PID $PID) was not running."
fi

rm -f "$PIDFILE"
