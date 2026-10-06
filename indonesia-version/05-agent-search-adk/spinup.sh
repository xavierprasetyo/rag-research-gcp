#!/usr/bin/env bash
# ==============================================================================
# spinup.sh - Spin up Skenario 5: Agent Search + ADK (Indonesia Version)
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
PYTHON="$SCRIPT_DIR/../../.venv/bin/python3"
PORT=8005

echo "================================================================================"
echo "  🚀 SPIN UP: Skenario 5 Agent Search + ADK (Indonesia Version)"
echo "  GCP Project: rag-research-sandbox | Framework: Google ADK"
echo "================================================================================"

echo "▶ 1. Starting server on port $PORT..."
fuser -k "$PORT"/tcp 2>/dev/null || true
nohup "$PYTHON" -m uvicorn server:app --host 0.0.0.0 --port "$PORT" > server.log 2>&1 &

for _ in {1..20}; do
    if curl --noproxy "*" -s "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then
        echo "   ✅ Server is up (logs: server.log)"
        break
    fi
    sleep 1
done

echo ""
echo "  🔌 API Docs : http://localhost:$PORT/docs"
echo "  📊 Health   : http://localhost:$PORT/api/health"
echo "  🧪 Eval     : $PYTHON eval_golden.py"
echo "  🧹 Teardown : ./teardown.sh"
echo "================================================================================"
