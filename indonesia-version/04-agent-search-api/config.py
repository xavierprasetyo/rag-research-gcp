import os
from pathlib import Path

# Google Cloud Project & Location
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "rag-research-sandbox")
LOCATION = os.getenv("DISCOVERY_ENGINE_LOCATION", "global")
COLLECTION_ID = "default_collection"

# Agent Search / Discovery Engine Resources
DATA_STORE_ID = "hr-faq-datastore-id"
ENGINE_ID = "hr-faq-search-id"
DATA_STORE_DISPLAY_NAME = "Cymbal HR FAQ Indonesia DataStore"
ENGINE_DISPLAY_NAME = "Cymbal HR FAQ Indonesia Search Engine"

# GCS Source (Shared with other scenarios)
BUCKET_NAME = f"{PROJECT_ID}-hr-docs"
GCS_PREFIX = "hr-docs/id/"
GCS_URI_PATTERN = f"gs://{BUCKET_NAME}/{GCS_PREFIX}*.pdf"

# Search Configuration
DEFAULT_TOP_K = 4
LANGUAGE_CODE = "id"

# Ports
BACKEND_PORT = 8004
GATEWAY_PORT = 8000

# Paths
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DOCS_DIR = BASE_DIR.parent / "source-documents"

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


