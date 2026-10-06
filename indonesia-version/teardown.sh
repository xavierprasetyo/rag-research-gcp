#!/usr/bin/env bash
# ==============================================================================
# teardown.sh - Master Teardown Script: Cymbal HR FAQ Indonesia Portal Suite
# ==============================================================================

set -eo pipefail

echo "================================================================================"
echo "  🧹 MASTER TEARDOWN: Cymbal HR FAQ Indonesia"
echo "================================================================================"

for PORT in 8000 8001 8002 8003 8004 8005 3000; do
    echo "▶ Stopping services on port $PORT..."
    fuser -k "$PORT"/tcp 2>/dev/null || true
done

echo "✅ All servers stopped."
