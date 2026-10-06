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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("server")

app = FastAPI(title="Cymbal HR FAQ Indonesia API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton retriever instance
retriever = RagEngineRetriever()


class QueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "tool"  # "tool" (native VertexRagStore), "retrieve" (rag.retrieval_query + own prompt)
    top_k: Optional[int] = 4


@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
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


@app.get("/api/status")
def get_status():
    try:
        from manage_collection import get_collection_info
        return get_collection_info()
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


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
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Pertanyaan tidak boleh kosong.")

    try:
        result = retriever.generate_answer(
            query=req.query.strip(),
            mode=req.mode or "tool",
            top_k=req.top_k or 4,
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
