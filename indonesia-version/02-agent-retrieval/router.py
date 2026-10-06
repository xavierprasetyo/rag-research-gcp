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
    COLLECTION_ID,
    PROJECT_ID,
    LOCATION,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    LLM_MODEL,
    LLM_LOCATION,
    GOLDEN_QUERIES,
)
from retriever import AgentRetriever

logger = logging.getLogger("scenario2_router")
router = APIRouter(tags=["Scenario 2: Agent Retrieval"])

_retriever: Optional[AgentRetriever] = None


def get_retriever() -> AgentRetriever:
    global _retriever
    if _retriever is None:
        _retriever = AgentRetriever()
    return _retriever


class QueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "hybrid"  # "hybrid", "semantic", "text"
    top_k: Optional[int] = 4
    corpus: Optional[str] = "id"



@router.get("/health")
def get_health():
    return {
        "status": "online",
        "scenario": "Scenario 2: Agent Retrieval (Serverless Collections)",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "collection_id": COLLECTION_ID,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimensions": EMBEDDING_DIMENSIONS,
        "llm_model": LLM_MODEL,
        "llm_location": LLM_LOCATION,
    }


@router.get("/status")
def get_status():
    try:
        r = get_retriever()
        collection = r.client.get_collection(name=r.collection_path)
        return {
            "collection_id": COLLECTION_ID,
            "status": "READY" if collection else "NOT_FOUND",
            "resource_name": collection.name if collection else None,
            "vector_schema": {
                "dense": {
                    "dimensions": EMBEDDING_DIMENSIONS,
                    "model": EMBEDDING_MODEL,
                }
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
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        r = get_retriever()
        corpus = req.corpus or "id"
        result = r.generate_answer(
            query=req.query.strip(),
            top_k=req.top_k or 4,
            search_mode=req.mode or "hybrid",
            corpus=corpus,
        )
        if "execution_mode" not in result:
            result["execution_mode"] = getattr(r, "_last_execution_mode", "live_gcp")
        return result
    except Exception as e:
        logger.error("Error processing query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
