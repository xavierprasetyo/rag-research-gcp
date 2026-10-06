#!/usr/bin/env bash
# ==============================================================================
# spinup.sh - Master Orchestration Script: Cymbal HR FAQ Indonesia Portal Suite
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================================"
echo "  🚀 MASTER SPIN UP: Cymbal HR FAQ Indonesia (5 Search Architectures Suite)"
echo "  GCP Project: rag-research-sandbox | Location: us-central1 / global"
echo "================================================================================"

# If an argument is given, spin up specific scenario standalone
if [ "$1" == "1" ]; then
    echo "▶ Launching S1 standalone (port 8001)..."
    exec ./01-vector-search-1.0/spinup.sh
elif [ "$1" == "2" ]; then
    echo "▶ Launching S2 standalone (port 8002)..."
    exec ./02-agent-retrieval/spinup.sh
elif [ "$1" == "3" ]; then
    echo "▶ Launching S3 standalone (port 8003)..."
    exec ./03-rag-engine/spinup.sh
elif [ "$1" == "4" ]; then
    echo "▶ Launching S4 standalone (port 8004)..."
    exec ./04-agent-search-api/spinup.sh
elif [ "$1" == "5" ]; then
    echo "▶ Launching S5 standalone (port 8005)..."
    exec ./05-agent-search-adk/spinup.sh
fi

echo "▶ Launching Unified Portal Gateway (Port 8000)..."
exec ./unified-portal/spinup.sh
