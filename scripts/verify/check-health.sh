#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
#  absorb-osp — API Health Check
#  Usage: check-health.sh <url> [expected-status]
# ──────────────────────────────────────────────────────────
set -euo pipefail
URL="${1:?Usage: check-health.sh <url> [expected-status]}"
EXPECTED="${2:-200}"
TIMEOUT=10

echo "🏥 Checking health: $URL"
echo "   Expected status: $EXPECTED"

START=$(date +%s%N)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$URL" 2>/dev/null || echo "000")
END=$(date +%s%N)
DURATION_MS=$(( (END - START) / 1000000 ))

if [ "$HTTP_CODE" = "$EXPECTED" ]; then
    echo "✅ Health check PASSED (HTTP $HTTP_CODE, ${DURATION_MS}ms)"
    exit 0
else
    echo "❌ Health check FAILED (HTTP $HTTP_CODE, expected $EXPECTED, ${DURATION_MS}ms)"
    exit 1
fi
