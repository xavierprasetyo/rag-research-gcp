#!/usr/bin/env bash
# ==============================================================================
# spinup.sh - Spin up Skenario 3: RAG Engine (Indonesia Version)
#
# Usage:  ./spinup.sh
#   - Creates the bucket, corpus, and import if missing (~3 min on a cold start;
#     instant if the corpus already exists)
#   - Starts the FastAPI server + React UI on http://localhost:8000
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
PYTHON="$SCRIPT_DIR/../../.venv/bin/python3"
PORT=8000

echo "  🚀 SPIN UP: RAG Engine (Indonesia Version) | rag-research-sandbox / us-central1"

echo "▶ 1. Checking frontend build..."
if [[ ! -d frontend/node_modules ]]; then (cd frontend && npm install); fi
if [[ ! -d frontend/dist ]]; then (cd frontend && npm run build); fi

echo "▶ 2. Ensuring bucket + corpus + imported files on GCP..."
"$PYTHON" manage_corpus.py create 2>&1 | grep -v "^DEBUG"

echo "▶ 3. Starting server on port $PORT..."
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
echo "  🌐 UI: http://localhost:$PORT   |   Eval: $PYTHON eval_golden.py"
echo "  🧹 When done: ./teardown.sh"
