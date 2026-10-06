#!/usr/bin/env bash
# ==============================================================================
# teardown.sh - Teardown Script for Agent Retrieval (Indonesia Version)
#
# Usage:
#   ./teardown.sh          # Stops local servers (Collection stays preserved at $0/hr)
#   ./teardown.sh --purge  # Complete cleanup (deletes collection hr-faq-id from GCP)
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Resolve virtual environment python
if [[ -f "$SCRIPT_DIR/../../.venv/bin/python3" ]]; then
    PYTHON="$SCRIPT_DIR/../../.venv/bin/python3"
elif [[ -f "$SCRIPT_DIR/.venv/bin/python3" ]]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python3"
else
    PYTHON="python3"
fi

PURGE_MODE=false
if [[ "$1" == "--purge" || "$1" == "--destroy-all" ]]; then
    PURGE_MODE=true
fi

echo "================================================================================"
echo "  🧹 TEARDOWN: Agent Retrieval / Vector Search 2.0 (Indonesia Version)"
echo "================================================================================"

# 1. Stop local web servers on ports 8000 & 3000
echo ""
echo "▶ 1. Stopping local servers (Port 8000 & Port 3000)..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
echo "   ✅ Local background processes terminated."

# 2. Serverless Status note
echo ""
echo "▶ 2. Google Cloud Infrastructure Status:"
echo "   Agent Retrieval is a fully Serverless architecture (no dedicated VM instances)."
echo "   Therefore, there are NO continuous hourly VM compute charges when idle."

# 3. Optional Purge Mode
if [ "$PURGE_MODE" = true ]; then
    echo ""
    echo "▶ 3. Purging GCP Collection (--purge mode enabled)..."
    "$PYTHON" manage_collection.py delete || true
    echo "   ✅ GCP Collection purged."
else
    echo ""
    echo "ℹ️  Collection metadata & DataObjects are preserved safely (\$0.00 idle compute)."
    echo "   To completely delete the Collection from GCP, re-run with: ./teardown.sh --purge"
fi

echo ""
echo "================================================================================"
echo "  ✅ Teardown Complete!"
echo "  To spin everything back up at any time, simply run:"
echo "     ./spinup.sh"
echo "================================================================================"
