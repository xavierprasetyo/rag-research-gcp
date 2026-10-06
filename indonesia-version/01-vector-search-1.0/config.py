import os
from pathlib import Path

# Google Cloud Project & Location
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "rag-research-sandbox")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Vertex AI Vector Search 1.0 Resources
INDEX_DISPLAY_NAME = "hr-faq-index-id"
ENDPOINT_DISPLAY_NAME = "hr-faq-endpoint-id"
DEPLOYED_INDEX_ID = "hr_faq_deployed_id"
MACHINE_TYPE = "e2-standard-16"
DISTANCE_MEASURE_TYPE = "DOT_PRODUCT_DISTANCE"
APPROXIMATE_NEIGHBORS_COUNT = 150
LEAF_NODE_EMBEDDING_COUNT = 500
LEAF_NODES_TO_SEARCH_PERCENT = 10

# Embedding Model Configuration
EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768
EMBEDDING_LOCATION = "global"

# Text Prefixes for gemini-embedding-2
DOC_PREFIX = "title: {source_doc} | text: {text}"
QUERY_PREFIX = "task: question answering | query: {query}"

# External Chunk Store: Google Cloud Firestore
FIRESTORE_DATABASE = "(default)"
FIRESTORE_COLLECTION = "hr-faq-chunks-id"

# LLM Generation Model
LLM_MODEL = "gemini-3.5-flash-lite"
LLM_LOCATION = "global"
SYSTEM_INSTRUCTION = (
    "Jawab dalam Bahasa Indonesia yang baku dan ringkas. "
    "Sebutkan nama dokumen sumber."
)

# Application & Networking Ports
BACKEND_PORT = 8001
FRONTEND_PORT = 3001

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


