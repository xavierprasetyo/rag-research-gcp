#!/usr/bin/env bash
# ==============================================================================
# spinup.sh - Single-Command Spin Up Script for Agent Retrieval (Indonesia Version)
#
# Usage:
#   ./spinup.sh             # Starts local servers & connects to Serverless Collection
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

echo "================================================================================"
echo "  🚀 SPIN UP: Agent Retrieval / Vector Search 2.0 (Indonesia Version)"
echo "  GCP Project: rag-research-sandbox | Region: us-central1 | Mode: Serverless"
echo "================================================================================"

# 1. Check Python virtual environment
echo ""
echo "▶ 1. Checking Python environment..."
echo "   Python executable: $PYTHON"
"$PYTHON" -c "import google.cloud.vectorsearch_v1beta, google.genai, fastapi, uvicorn; print('   ✅ Core Python packages verified.')"

# 2. Check Frontend Build
echo ""
echo "▶ 2. Checking Frontend build..."
if [[ ! -d "frontend/node_modules" ]]; then
    echo "   Installing frontend dependencies..."
    (cd frontend && npm install)
fi
if [[ ! -d "frontend/dist" ]]; then
    echo "   Building frontend production bundle..."
    (cd frontend && npm run build)
fi
echo "   ✅ Frontend ready."

# 3. Verify Serverless Collection on GCP
echo ""
echo "▶ 3. Verifying Agent Retrieval Collection on GCP..."
"$PYTHON" -c "
from manage_collection import get_collection_info
import sys, subprocess

info = get_collection_info()
if not info.get('exists'):
    print('   Collection hr-faq-id not found. Running ingestion...')
    subprocess.run([sys.executable, 'ingest.py'], check=True)
else:
    print(f'   ✅ Collection ready: {info.get(\"collection_id\")} ({info.get(\"chunk_count\")} chunks indexed)')
"

# 4. Clear lingering processes on ports 8000 & 3000
echo ""
echo "▶ 4. Freeing ports 8000 & 3000..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true

# 5. Start FastAPI Backend Server
echo ""
echo "▶ 5. Starting FastAPI Backend server on port 8000..."
nohup "$PYTHON" server.py > server.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID (logs: server.log)"

# 6. Start Vite Frontend Server
echo ""
echo "▶ 6. Starting Vite Frontend server on port 3000..."
(cd frontend && nohup npx vite --host 127.0.0.1 --port 3000 --strictPort > ../frontend.log 2>&1 &)
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID (logs: frontend.log)"

# 7. Health Check Wait Loop
echo ""
echo "▶ 7. Waiting for servers to initialize..."
for i in {1..15}; do
    if curl --noproxy "*" -s http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
        echo "   ✅ Backend server responded successfully (HTTP 200)!"
        break
    fi
    sleep 1
done

echo ""
echo "================================================================================"
echo "  🎉 Application is UP and READY!"
echo "================================================================================"
echo ""
echo "  🌐 Interactive Frontend UI : http://localhost:3000"
echo "  🔌 FastAPI Server & Docs   : http://localhost:8000/docs"
echo "  📊 Live Health Check       : http://localhost:8000/api/health"
echo ""
echo "  💡 Useful Commands:"
echo "     • View live status      : $PYTHON manage_collection.py status"
echo "     • Run 4-query eval suite: $PYTHON eval_golden.py"
echo "     • Tear down servers     : ./teardown.sh"
echo "================================================================================"
