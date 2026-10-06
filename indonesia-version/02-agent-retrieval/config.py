import os
from pathlib import Path

# Google Cloud Project & Location
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "rag-research-sandbox")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Collection & Retrieval Resource Config
COLLECTION_ID = "hr-faq-id"
COLLECTION_ID_EN = "hr-faq-en"
TOP_K = 4
EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768
TEXT_TEMPLATE = "title: {source_doc} | text: {text}"

LLM_MODEL = "gemini-3.5-flash-lite"
LLM_LOCATION = "global"
SYSTEM_INSTRUCTION = (
    "Jawab dalam Bahasa Indonesia yang baku dan ringkas. "
    "Sebutkan nama dokumen sumber."
)
SYSTEM_INSTRUCTION_EN = (
    "You are an HR policy assistant for Cymbal Global. Answer concisely and accurately "
    "in English based ONLY on the provided policy excerpts. Always cite the source document."
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DOCS_DIR = BASE_DIR.parent / "source-documents"
CHUNKS_CACHE_FILE = BASE_DIR / "chunks_cache.json"
CHUNKS_CACHE_FILE_EN = BASE_DIR / "chunks_cache_en.json"

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


def get_documents_by_corpus(corpus: str = "id") -> list[dict]:
    """Return all 10 HR policy documents for the selected corpus ('id' or 'en')."""
    if corpus == "en":
        return DOCUMENTS_EN
    return DOCUMENTS_ID


GOLDEN_QUERIES = GOLDEN_QUERIES_ID
