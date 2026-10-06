import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

CURRENT_DIR = Path(__file__).resolve().parent
import sys
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from config import (
    PROJECT_ID,
    LOCATION,
    INDEX_DISPLAY_NAME,
    ENDPOINT_DISPLAY_NAME,
    DEPLOYED_INDEX_ID,
    MACHINE_TYPE,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    FIRESTORE_COLLECTION,
    FIRESTORE_DATABASE,
    LLM_MODEL,
    LLM_LOCATION,
    BACKEND_PORT,
    GOLDEN_QUERIES,
)
from retriever import VS1Retriever
from manage_index import find_index, find_endpoint, get_firestore_chunk_count

logger = logging.getLogger("scenario1_router")
router = APIRouter(tags=["Scenario 1: Vector Search 1.0"])

_retriever: Optional[VS1Retriever] = None


def get_retriever() -> VS1Retriever:
    global _retriever
    if _retriever is None:
        _retriever = VS1Retriever()
    return _retriever


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4
    corpus: Optional[str] = "id"


@router.get("/health")
def get_health():
    is_deployed = False
    try:
        r = get_retriever()
        is_deployed = r.is_endpoint_deployed()
    except Exception as e:
        logger.warning("Could not check endpoint deployment status: %s", e)

    return {
        "status": "online",
        "scenario": "Scenario 1: Vector Search 1.0",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "index_display_name": INDEX_DISPLAY_NAME,
        "endpoint_display_name": ENDPOINT_DISPLAY_NAME,
        "deployed_index_id": DEPLOYED_INDEX_ID,
        "is_deployed": is_deployed,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimensions": EMBEDDING_DIMENSIONS,
        "firestore_collection": FIRESTORE_COLLECTION,
        "llm_model": LLM_MODEL,
        "llm_location": LLM_LOCATION,
        "port": BACKEND_PORT,
    }


@router.get("/status")
def get_status():
    try:
        index = find_index()
        endpoint = find_endpoint()
        firestore_count = get_firestore_chunk_count()

        is_deployed = False
        deployed_indexes = []
        if endpoint:
            for d in endpoint.deployed_indexes:
                deployed_indexes.append({
                    "id": d.id,
                    "index": d.index,
                    "display_name": getattr(d, "display_name", ""),
                })
                if d.id == DEPLOYED_INDEX_ID:
                    is_deployed = True

        return {
            "index": {
                "name": INDEX_DISPLAY_NAME,
                "exists": index is not None,
                "resource_name": index.resource_name if index else None,
            },
            "endpoint": {
                "name": ENDPOINT_DISPLAY_NAME,
                "exists": endpoint is not None,
                "resource_name": endpoint.resource_name if endpoint else None,
                "is_deployed": is_deployed,
                "deployed_indexes": deployed_indexes,
                "machine_type": MACHINE_TYPE,
            },
            "firestore": {
                "database": FIRESTORE_DATABASE,
                "collection": FIRESTORE_COLLECTION,
                "chunk_count": firestore_count,
            },
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


@router.get("/golden-queries")
def get_golden_queries(corpus: Optional[str] = "id"):
    from config import GOLDEN_QUERIES_EN
    if corpus == "en":
        return {"queries": GOLDEN_QUERIES_EN}
    return {"queries": GOLDEN_QUERIES}


@router.get("/documents")
def get_documents(corpus: Optional[str] = "id"):
    from config import DOCUMENTS_ID, DOCUMENTS_EN
    if corpus == "en":
        return {"documents": DOCUMENTS_EN}
    return {"documents": DOCUMENTS_ID}


@router.get("/benchmark")
def get_benchmark():
    eval_file = CURRENT_DIR / "eval_results.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            return {"results": json.load(f)}
    return {"results": []}


@router.post("/query")
def process_query(req: QueryRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        retriever = get_retriever()
        corpus = req.corpus or "id"
        result = retriever.generate_answer(
            query=req.query.strip(),
            top_k=req.top_k or 4,
            corpus=corpus,
        )
        if "execution_mode" not in result:
            result["execution_mode"] = (
                "live_gcp" if result.get("is_live_vm") else "local_cache_fallback"
            )
        return result
    except RuntimeError as re:
        logger.error("Runtime error during query: %s", re)
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.exception("Unexpected error processing query: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

