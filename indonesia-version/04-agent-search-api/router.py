import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import (
    PROJECT_ID,
    LOCATION,
    COLLECTION_ID,
    DATA_STORE_ID,
    ENGINE_ID,
    LANGUAGE_CODE,
    GOLDEN_QUERIES,
    GOLDEN_QUERIES_EN,
    DOCUMENTS_ID,
    DOCUMENTS_EN,
)
from retriever import AgentSearchRetriever
from manage_datastore import get_datastore_info

router = APIRouter(tags=["Scenario 4: Agent Search API"])

_retriever: Optional[AgentSearchRetriever] = None


def get_retriever() -> AgentSearchRetriever:
    global _retriever
    if _retriever is None:
        _retriever = AgentSearchRetriever()
    return _retriever


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4
    corpus: Optional[str] = "id"


@router.get("/health")
def get_health():
    return {
        "status": "online",
        "scenario": "Scenario 4: Agent Search API",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "collection_id": COLLECTION_ID,
        "datastore_id": DATA_STORE_ID,
        "engine_id": ENGINE_ID,
        "language_code": LANGUAGE_CODE,
    }


@router.get("/status")
def get_status():
    try:
        return get_datastore_info()
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


@router.get("/golden-queries")
def get_golden_queries(corpus: Optional[str] = "id"):
    if corpus == "en":
        return {"queries": GOLDEN_QUERIES_EN}
    return {"queries": GOLDEN_QUERIES}


@router.get("/documents")
def get_documents(corpus: Optional[str] = "id"):
    if corpus == "en":
        return {"documents": DOCUMENTS_EN}
    return {"documents": DOCUMENTS_ID}


@router.get("/benchmark")
def get_benchmark():
    eval_file = Path(__file__).parent / "eval_results.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            return {"results": json.load(f)}
    return {"results": []}


@router.post("/query")
def process_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Pertanyaan tidak boleh kosong.")

    try:
        r = get_retriever()
        corpus = req.corpus or "id"
        result = r.search_and_answer(query=req.query.strip(), top_k=req.top_k or 4, corpus=corpus)
        response_payload = {
            **result,
            "execution_mode": result.get("execution_mode", "live_gcp"),
        }
        if "fallback_reason" in result and result["fallback_reason"] is not None:
            response_payload["fallback_reason"] = result["fallback_reason"]
        return response_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

