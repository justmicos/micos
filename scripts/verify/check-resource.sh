#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
#  absorb-osp — Resource Usage Monitor
#  Usage: check-resource.sh <pid|port> [duration_seconds]
# ──────────────────────────────────────────────────────────
set -euo pipefail

TARGET="${1:?Usage: check-resource.sh <pid|port> [seconds]}"
DURATION="${2:-5}"

echo "📊 Monitoring resource usage for: $TARGET"
echo "   Duration: ${DURATION}s"
echo ""

# Determine if target is PID or port
if [[ "$TARGET" =~ ^[0-9]+$ ]]; then
    # It's a PID
    if ! kill -0 "$TARGET" 2>/dev/null; then
        echo "❌ Process $TARGET not found"
        exit 1
    fi
    echo "   PID: $TARGET"
    echo ""
    echo "   CPU%  MEM%  RSS(MB)  VSZ(MB)  COMMAND"
    echo "   ─────────────────────────────────────────"
    for i in $(seq 1 "$DURATION"); do
        ps -p "$TARGET" -o %cpu,%mem,rss,vsz,comm --no-headers 2>/dev/null || true
        sleep 1
    done
elif [[ "$TARGET" =~ ^[0-9]+$ ]]; then
    # Port number - find PID
    PID=$(lsof -ti :"$TARGET" 2>/dev/null || netstat -ano | grep ":$TARGET " | awk '{print $5}' | head -1)
    if [ -z "$PID" ]; then
        echo "❌ No process found on port $TARGET"
        exit 1
    fi
    echo "   Port $TARGET → PID $PID"
    echo ""
    for i in $(seq 1 "$DURATION"); do
        ps -p "$PID" -o %cpu,%mem,rss,vsz,comm --no-headers 2>/dev/null || true
        sleep 1
    done
else
    # Assume it's a command name
    echo "   Pattern: $TARGET"
    ps aux | grep -v grep | grep "$TARGET" | awk '{print $3, $4, $5, $6, $11}' || echo "   (no matching process)"
fi

echo ""
echo "✅ Resource monitoring complete"
