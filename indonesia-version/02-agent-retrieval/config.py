import os
from pathlib import Path

# Google Cloud Project & Location
PROJECT_ID = "rag-research-sandbox"
LOCATION = "us-central1"

# Collection & Retrieval Resource Config
COLLECTION_ID = "hr-faq-id"
EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768
TEXT_TEMPLATE = "title: {source_doc} | text: {text}"

LLM_MODEL = "gemini-3.5-flash-lite"
LLM_LOCATION = "global"
SYSTEM_INSTRUCTION = (
    "Jawab dalam Bahasa Indonesia yang baku dan ringkas. "
    "Sebutkan nama dokumen sumber."
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DOCS_DIR = BASE_DIR.parent / "source-documents"
CHUNKS_CACHE_FILE = BASE_DIR / "chunks_cache.json"

# Chunking Parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80

# Golden Queries & Document Definitions imported from shared_corpus_metadata
import sys
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))

from shared_corpus_metadata import (
    DOCUMENTS_ID,
    DOCUMENTS_EN,
    GOLDEN_QUERIES_ID,
    GOLDEN_QUERIES_EN,
)

GOLDEN_QUERIES = GOLDEN_QUERIES_ID


