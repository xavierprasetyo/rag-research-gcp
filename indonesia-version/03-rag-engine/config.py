import os
from pathlib import Path

# Google Cloud Project & Location
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "rag-research-sandbox")
LOCATION = "us-central1"

# GCS source (RAG Engine imports straight from the bucket)
BUCKET_NAME = f"{PROJECT_ID}-hr-docs"
GCS_PREFIX = "hr-docs/id/"
GCS_URI = f"gs://{BUCKET_NAME}/{GCS_PREFIX}"

# RagCorpus config. The embedding model is fixed for the corpus lifetime, and
# RAG Engine rejects Gemini embedding models (see PRD section 2).
CORPUS_DISPLAY_NAME = "hr-faq-rag-id"
EMBEDDING_MODEL = "text-multilingual-embedding-002"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 100

# Retrieval
TOP_K = 4
SIMILARITY_TOP_K = TOP_K

LLM_MODEL = "gemini-3.5-flash-lite"
LLM_LOCATION = "global"
SYSTEM_INSTRUCTION = (
    "Jawab dalam Bahasa Indonesia yang baku dan ringkas. "
    "Sebutkan nama dokumen sumber."
)
SYSTEM_INSTRUCTION_EN = (
    "You are an HR policy assistant for Cymbal Global. "
    "Answer accurately in English based ONLY on the retrieved HR policy contexts. "
    "Cite the source document name."
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DOCS_DIR = BASE_DIR.parent / "source-documents"
CORPUS_STATE_FILE = BASE_DIR / "corpus.json"  # stores the corpus resource name

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


