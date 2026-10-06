#!/usr/bin/env bash
# ==============================================================================
# teardown.sh - Teardown Unified Portal Gateway (Port 8000)
# ==============================================================================

set -eo pipefail

PORT=8000
echo "▶ Stopping gateway server on port $PORT..."
fuser -k "$PORT"/tcp 2>/dev/null || true
echo "✅ Gateway stopped."
