#!/usr/bin/env bash
# ==============================================================================
# teardown.sh - Teardown Skenario 4 (Indonesia Version)
# ==============================================================================

set -eo pipefail

PORT=8004
echo "▶ Stopping server on port $PORT..."
fuser -k "$PORT"/tcp 2>/dev/null || true
echo "✅ Server stopped."
