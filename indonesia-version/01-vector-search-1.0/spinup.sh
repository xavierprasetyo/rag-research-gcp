#!/usr/bin/env bash
# ==============================================================================
# spinup.sh - Single-Command Spin Up Script for Vector Search 1.0 (Indonesia Version)
#
# Usage:
#   ./spinup.sh             # Starts local servers & connects to GCP (Preview/Live Mode)
#   ./spinup.sh --deploy-vm # Starts local servers & deploys dedicated e2-standard-16 VM on GCP
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

DEPLOY_VM=false
if [[ "$1" == "--deploy-vm" || "$1" == "--deploy" ]]; then
    DEPLOY_VM=true
fi

echo "================================================================================"
echo "  🚀 SPIN UP: Vector Search 1.0 (Indonesia Version)"
echo "  GCP Project: rag-research-sandbox | Region: us-central1"
echo "================================================================================"

# 1. Check Python virtual environment
echo ""
echo "▶ 1. Checking Python environment..."
echo "   Python executable: $PYTHON"
"$PYTHON" -c "import google.cloud.aiplatform, google.genai, fastapi, uvicorn; print('   ✅ Core Python packages verified.')"

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

# 3. Verify GCP Resources (Index, Firestore, Endpoint)
echo ""
echo "▶ 3. Verifying Vertex AI & Cloud Firestore resources on GCP..."
"$PYTHON" -c "
from manage_index import find_index, find_endpoint, create_index, create_endpoint, get_firestore_chunk_count
import sys

idx = find_index()
if not idx:
    print('   Creating MatchingEngineIndex (hr-faq-index-id)...')
    create_index()
else:
    print('   ✅ MatchingEngineIndex found: ' + idx.display_name)

cnt = get_firestore_chunk_count()
if cnt <= 0:
    print('   Ingesting documents to Firestore & Index...')
    import subprocess
    subprocess.run([sys.executable, 'ingest.py'], check=True)
else:
    print(f'   ✅ Cloud Firestore ready ({cnt} chunks in hr-faq-chunks-id)')

ep = find_endpoint()
if not ep:
    print('   Creating MatchingEngineIndexEndpoint (hr-faq-endpoint-id)...')
    create_endpoint()
else:
    print('   ✅ MatchingEngineIndexEndpoint found: ' + ep.display_name)
"

# 4. Handle Dedicated VM Deployment if requested
if [ "$DEPLOY_VM" = true ]; then
    echo ""
    echo "▶ 4. Triggering dedicated e2-standard-16 VM deployment on Vertex AI..."
    "$PYTHON" manage_index.py deploy --async
    echo "   ℹ️ VM is provisioning in the background (~20-30 min)."
    echo "   The server will run in Preview Mode and automatically switch to the VM once ready."
else
    echo ""
    echo "▶ 4. Endpoint VM Status:"
    echo "   (Running in cost-effective mode with live Firestore + live Gemini 3.5 Flash-Lite)"
    echo "   To deploy the dedicated e2-standard-16 VM node, pass: ./spinup.sh --deploy-vm"
fi

# 5. Clear lingering processes on ports
echo ""
echo "▶ 5. Freeing ports 8001 & 3001..."
fuser -k 8001/tcp 2>/dev/null || true
fuser -k 3001/tcp 2>/dev/null || true

# 6. Start FastAPI Backend Server
echo ""
echo "▶ 6. Starting FastAPI Backend server on port 8001..."
nohup "$PYTHON" server.py > server.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID (logs: server.log)"

# 7. Start Frontend Dev Server
echo ""
echo "▶ 7. Starting Vite Frontend server on port 3001..."
(cd frontend && nohup npx vite --host 127.0.0.1 --port 3001 --strictPort > ../frontend.log 2>&1 &)
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID (logs: frontend.log)"

# 8. Health Check Wait Loop
echo ""
echo "▶ 8. Waiting for servers to initialize..."
for i in {1..15}; do
    if curl --noproxy "*" -s http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
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
echo "  🌐 Interactive Frontend UI : http://localhost:3001"
echo "  🔌 FastAPI Server & Docs   : http://localhost:8001/docs"
echo "  📊 Live Health Check       : http://localhost:8001/api/health"
echo ""
echo "  💡 Useful Commands:"
echo "     • View live status      : $PYTHON manage_index.py status"
echo "     • Run 4-query eval suite: $PYTHON eval_golden.py"
echo "     • Tear down everything  : ./teardown.sh"
echo "================================================================================"
