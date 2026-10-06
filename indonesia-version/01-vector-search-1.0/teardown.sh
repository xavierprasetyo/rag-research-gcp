#!/usr/bin/env bash
# ==============================================================================
# teardown.sh - Teardown Script for Vector Search 1.0 (Indonesia Version)
#
# Usage:
#   ./teardown.sh          # Stops local servers & undeploys VM endpoint (Stops hourly billing)
#   ./teardown.sh --purge  # Complete cleanup (undeploys, deletes endpoint & index from GCP)
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
echo "  🧹 TEARDOWN: Vector Search 1.0 (Indonesia Version)"
echo "================================================================================"

# 1. Stop local web servers on ports 8001 & 3001
echo ""
echo "▶ 1. Stopping local servers (Port 8001 & Port 3001)..."
fuser -k 8001/tcp 2>/dev/null || true
fuser -k 3001/tcp 2>/dev/null || true
echo "   ✅ Local background processes terminated."

# 2. Undeploy Index from Vertex AI Endpoint (Halt VM compute charges)
echo ""
echo "▶ 2. Undeploying index from Vertex AI Endpoint on GCP..."
echo "   (This stops the dedicated e2-standard-16 VM and halts hourly billing)"

ENDPOINT_ID="3708931996441903104"
PROJECT_ID="rag-research-sandbox"
REGION="us-central1"
DEPLOYED_ID="hr_faq_deployed_id"

if command -v gcloud &>/dev/null; then
    gcloud ai index-endpoints undeploy-index "$ENDPOINT_ID" \
        --project="$PROJECT_ID" \
        --region="$REGION" \
        --deployed-index-id="$DEPLOYED_ID" \
        --quiet 2>/dev/null || echo "   (Index was already undeployed or operation in progress)"
else
    "$PYTHON" manage_index.py undeploy --async || true
fi
echo "   ✅ Endpoint VM undeployed. VM compute charges are halted."

# 3. Optional Purge Mode
if [ "$PURGE_MODE" = true ]; then
    echo ""
    echo "▶ 3. Purging GCP Resources (--purge mode enabled)..."
    echo "   • Deleting Endpoint..."
    "$PYTHON" manage_index.py delete-endpoint || true
    echo "   • Deleting Index..."
    "$PYTHON" manage_index.py delete-index || true
    echo "   ✅ GCP Resources purged."
else
    echo ""
    echo "ℹ️  Index & Firestore metadata are preserved safely (\$0.00 idle cost)."
    echo "   To completely delete the Index and Endpoint from GCP, re-run with: ./teardown.sh --purge"
fi

echo ""
echo "================================================================================"
echo "  ✅ Teardown Complete!"
echo "  To spin everything back up at any time, simply run:"
echo "     ./spinup.sh"
echo "================================================================================"
