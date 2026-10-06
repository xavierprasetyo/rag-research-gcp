#!/usr/bin/env bash
# ==============================================================================
# teardown.sh - Teardown Skenario 5 (Indonesia Version)
# ==============================================================================

set -eo pipefail

PORT=8005
echo "▶ Stopping server on port $PORT..."
fuser -k "$PORT"/tcp 2>/dev/null || true
echo "✅ Server stopped."
