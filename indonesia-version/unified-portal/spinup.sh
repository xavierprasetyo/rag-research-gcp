#!/usr/bin/env bash
# ==============================================================================
# spinup.sh - Spin up Unified Portal Gateway (Port 8000)
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
PYTHON="$SCRIPT_DIR/../../.venv/bin/python3"
PORT=8000

echo "================================================================================"
echo "  🚀 SPIN UP: Cymbal HR FAQ Unified Portal Gateway (Port $PORT)"
echo "  Mounting S1, S2, S3, S4, S5 + Frontend Single Page Application"
echo "================================================================================"

# Build frontend if dist doesn't exist
if [ ! -d "frontend/dist" ]; then
    echo "▶ Building frontend dist..."
    (cd frontend && npm run build)
fi

echo "▶ Starting gateway server on port $PORT..."
fuser -k "$PORT"/tcp 2>/dev/null || true
nohup "$PYTHON" -m uvicorn server:app --host 0.0.0.0 --port "$PORT" > server.log 2>&1 &

for _ in {1..20}; do
    if curl --noproxy "*" -s "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then
        echo "   ✅ Gateway is up (logs: server.log)"
        break
    fi
    sleep 1
done

echo ""
echo "  🌐 Portal UI : http://localhost:$PORT"
echo "  🔌 API Docs  : http://localhost:$PORT/docs"
echo "  📊 Overview  : http://localhost:$PORT/api/overview"
echo "  🧹 Teardown  : ./teardown.sh"
echo "================================================================================"
