import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import (
    COLLECTION_ID,
    PROJECT_ID,
    LOCATION,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    LLM_MODEL,
    LLM_LOCATION,
    GOLDEN_QUERIES,
    GOLDEN_QUERIES_EN,
    get_documents_by_corpus,
)
from retriever import AgentRetriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("server")

app = FastAPI(title="Cymbal HR FAQ Indonesia API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy singleton retriever instance
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


@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "collection_id": COLLECTION_ID,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimensions": EMBEDDING_DIMENSIONS,
        "llm_model": LLM_MODEL,
        "llm_location": LLM_LOCATION,
    }


@app.get("/api/status")
def get_status():
    try:
        from manage_collection import get_collection_info
        return get_collection_info()
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


@app.get("/api/golden-queries")
def get_golden_queries(corpus: str = "id"):
    if corpus == "en":
        return {"queries": GOLDEN_QUERIES_EN}
    return {"queries": GOLDEN_QUERIES}


@app.get("/api/documents")
def get_documents(corpus: str = "id"):
    docs = get_documents_by_corpus(corpus)
    return {"documents": docs}


@app.get("/api/benchmark")
def get_benchmark():
    eval_file = Path(__file__).parent / "eval_results.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            return {"results": json.load(f)}
    return {"results": []}


@app.post("/api/query")
def process_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Pertanyaan tidak boleh kosong.")

    try:
        r = get_retriever()
        result = r.generate_answer(
            query=req.query.strip(),
            top_k=req.top_k or 4,
            search_mode=req.mode or "hybrid",
            corpus=req.corpus or "id",
        )
        return result
    except Exception as e:
        logger.error("Error generating answer: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# Serve React build if frontend/dist exists
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")
