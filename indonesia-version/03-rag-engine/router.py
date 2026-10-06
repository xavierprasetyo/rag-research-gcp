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
    CORPUS_DISPLAY_NAME,
    PROJECT_ID,
    LOCATION,
    EMBEDDING_MODEL,
    GCS_URI,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    LLM_MODEL,
    LLM_LOCATION,
    GOLDEN_QUERIES,
)
from retriever import RagEngineRetriever

logger = logging.getLogger("scenario3_router")
router = APIRouter(tags=["Scenario 3: RAG Engine"])

_retriever: Optional[RagEngineRetriever] = None


def get_retriever() -> RagEngineRetriever:
    global _retriever
    if _retriever is None:
        _retriever = RagEngineRetriever()
    return _retriever


class QueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "tool"  # "tool" (native VertexRagStore), "retrieve" (rag.retrieval_query)
    top_k: Optional[int] = 4
    corpus: Optional[str] = "id"



@router.get("/health")
def get_health():
    return {
        "status": "online",
        "scenario": "Scenario 3: RAG Engine (Managed File Corpus)",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "corpus": CORPUS_DISPLAY_NAME,
        "source": GCS_URI,
        "embedding_model": EMBEDDING_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "llm_model": LLM_MODEL,
        "llm_location": LLM_LOCATION,
    }


@router.get("/status")
def get_status():
    try:
        r = get_retriever()
        info = r.get_corpus_info()
        return info
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
        result = r.generate_answer(
            query=req.query.strip(),
            mode=req.mode or "tool",
            top_k=req.top_k or 4,
        )
        return result
    except Exception as e:
        logger.error("Error processing query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
