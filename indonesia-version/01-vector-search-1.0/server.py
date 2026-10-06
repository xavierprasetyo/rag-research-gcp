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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("server")

app = FastAPI(title="Cymbal HR FAQ Indonesia API — Vector Search 1.0", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy instance of VS1Retriever
_retriever: Optional[VS1Retriever] = None


def get_retriever() -> VS1Retriever:
    global _retriever
    if _retriever is None:
        _retriever = VS1Retriever()
    return _retriever


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4


@app.get("/api/health")
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


@app.get("/api/status")
def get_status():
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


@app.get("/api/golden-queries")
def get_golden_queries():
    return {"queries": GOLDEN_QUERIES}


@app.get("/api/documents")
def get_documents():
    docs = [
        {
            "filename": "01_Kebijakan_Cuti_Karyawan.pdf",
            "title": "Kebijakan Cuti Karyawan",
            "code": "HC-KBJ-011/2026",
            "description": "Cuti tahunan bertingkat (12-18 hari), cuti bersama, cuti melahirkan (3 bulan), cuti pendampingan persalinan (5 hari kerja), dan cuti besar 1 bulan.",
            "test_target": "Pencarian Semantik Murni (Q1-ID)",
        },
        {
            "filename": "02_Panduan_Tunjangan_dan_Kesehatan_2026.pdf",
            "title": "Panduan Tunjangan dan Kesehatan 2026",
            "code": "HC-TNJ-002/2026",
            "description": "Tabel manfaat plafon rawat inap, rawat jalan, persalinan normal/caesar, kacamata per level jabatan (Staf, Supervisor, Manajer, Direktur), BPJS, dan THR.",
            "test_target": "Parsing Data Tabel Multikolom (Q3-ID)",
        },
        {
            "filename": "03_Kebijakan_Perjalanan_Dinas_dan_Reimburse.pdf",
            "title": "Kebijakan Perjalanan Dinas & Reimburse",
            "code": "FIN-KBJ-402/2026",
            "description": "Surat Perintah Perjalanan Dinas (SPPD), Formulir PDN-402B (batas pengajuan 14 hari kalender), uang harian wilayah I-III, dan aturan kuitansi.",
            "test_target": "Pencarian Kata Kunci & Kode Formulir (Q2-ID)",
        },
        {
            "filename": "04_FAQ_WFH_WFA_dan_Tunjangan_Peralatan.pdf",
            "title": "FAQ WFH, WFA, dan Tunjangan Peralatan",
            "code": "HC-FAQ-220/2026",
            "description": "Batas WFH (2 hari/minggu), WFA dalam negeri (maksimal 20 hari kerja/tahun, pengajuan H-7), WFA luar negeri (10 hari, izin Direktur/IT), fasilitas kerja.",
            "test_target": "Istilah Campuran & Kebijakan Hybrid (Q4-ID)",
        },
    ]
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
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        retriever = get_retriever()
        result = retriever.generate_answer(query=req.query.strip(), top_k=req.top_k or 4)
        return result
    except RuntimeError as re:
        logger.error("Runtime error during query: %s", re)
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.exception("Unexpected error processing query: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Serve Static Frontend Assets (Vite dist)
FRONTEND_DIST_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

if FRONTEND_DIST_DIR.exists() and (FRONTEND_DIST_DIR / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_react_app(full_path: str):
        target = FRONTEND_DIST_DIR / full_path
        if target.exists() and target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_DIST_DIR / "index.html"))
else:
    @app.get("/")
    def index_fallback():
        return {
            "message": "Cymbal HR FAQ Indonesia API (Vector Search 1.0) is running.",
            "frontend": "Frontend dist not yet built. Run 'npm run build' in frontend/ or run Vite dev server on port 3001.",
            "endpoints": [
                "/api/health",
                "/api/status",
                "/api/golden-queries",
                "/api/query (POST)",
                "/docs",
            ],
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
