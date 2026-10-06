#!/usr/bin/env bash
# ==============================================================================
# teardown.sh - Tear down Skenario 3: RAG Engine (Indonesia Version)
#
# Usage:
#   ./teardown.sh          # Stops the server, deletes the RagCorpus and the GCS bucket
#   ./teardown.sh --keep   # Stops the server only (corpus + bucket stay, they keep storing data)
#
# Leaves in place (no charge): the Serverless RAG Engine mode and the
# roles/vectorsearch.admin grant to the RAG service agent.
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
PYTHON="$SCRIPT_DIR/../../.venv/bin/python3"

echo "  🧹 TEARDOWN: RAG Engine (Indonesia Version)"

echo "▶ 1. Stopping local server (port 8000)..."
fuser -k 8000/tcp 2>/dev/null || true

if [[ "$1" == "--keep" ]]; then
    echo "ℹ️  Corpus and bucket preserved. Run ./teardown.sh to delete them."
else
    echo "▶ 2. Deleting RagCorpus and GCS bucket..."
    "$PYTHON" manage_corpus.py delete --bucket 2>&1 | grep -v "^DEBUG"
fi

echo "  ✅ Done. Spin back up any time with ./spinup.sh"
