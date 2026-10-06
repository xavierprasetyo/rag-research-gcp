import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("gateway_server")

PORTAL_DIR = Path(__file__).resolve().parent
ROOT_DIR = PORTAL_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared_corpus_metadata import (
    DOCUMENTS_ID,
    DOCUMENTS_EN,
    GOLDEN_QUERIES_ID,
    GOLDEN_QUERIES_EN,
)

app = FastAPI(
    title="Cymbal HR FAQ Indonesia — Unified Portal Gateway",
    description="Gateway server untuk 5 arsitektur retrieval & search di Google Cloud",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_router(scenario_dir_name: str, module_alias: str):
    """Memuat router.py dari folder skenario secara terisolasi tanpa tabrakan modul."""
    dir_path = ROOT_DIR / scenario_dir_name
    router_file = dir_path / "router.py"
    if not router_file.exists():
        logger.warning(f"Router file not found: {router_file}")
        return None

    # Simpan snapshot sys.modules untuk isolasi config & retriever
    saved_modules = {k: v for k, v in sys.modules.items() if k in ["config", "retriever", "manage_index", "manage_collection", "manage_corpus", "manage_datastore", "tools", "agent"]}
    for k in saved_modules:
        del sys.modules[k]

    sys.path.insert(0, str(dir_path))
    try:
        spec = importlib.util.spec_from_file_location(module_alias, str(router_file))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_alias] = mod
        spec.loader.exec_module(mod)
        return mod.router
    except Exception as e:
        logger.error(f"Gagal memuat router untuk {scenario_dir_name}: {e}")
        return None
    finally:
        if str(dir_path) in sys.path:
            sys.path.remove(str(dir_path))
        # Kembalikan modul yang disimpan
        sys.modules.update(saved_modules)


# Mount semua router skenario di bawah prefix /api/s1 s/d /api/s5
s1_router = load_router("01-vector-search-1.0", "s1_mod")
if s1_router:
    app.include_router(s1_router, prefix="/api/s1")

s2_router = load_router("02-agent-retrieval", "s2_mod")
if s2_router:
    app.include_router(s2_router, prefix="/api/s2")

s3_router = load_router("03-rag-engine", "s3_mod")
if s3_router:
    app.include_router(s3_router, prefix="/api/s3")

s4_router = load_router("04-agent-search-api", "s4_mod")
if s4_router:
    app.include_router(s4_router, prefix="/api/s4")

s5_router = load_router("05-agent-search-adk", "s5_mod")
if s5_router:
    app.include_router(s5_router, prefix="/api/s5")


@app.get("/api/health")
def gateway_health():
    import os
    return {
        "status": "online",
        "service": "Cymbal HR FAQ Unified Gateway",
        "scenarios_mounted": {
            "s1": s1_router is not None,
            "s2": s2_router is not None,
            "s3": s3_router is not None,
            "s4": s4_router is not None,
            "s5": s5_router is not None,
        },
        "port": int(os.environ.get("PORT", 8080)),
    }


@app.get("/api/overview")
def get_overview(corpus: Optional[str] = "id"):
    """Returns architecture comparisons, trade-off matrix, and golden query fit."""
    fit_key = "golden_query_fit_en" if corpus == "en" else "golden_query_fit_id"

    scenarios = [
        {
            "id": "s1",
            "name": "Vector Search 1.0",
            "subtitle": "Dedicated ANN Index + Firestore Payload",
            "badge": "Infrastructure Control",
            "description": "Classic custom vector architecture featuring ScaNN-based Approximate Nearest Neighbor index on Vertex AI and external text chunk payload storage in Cloud Firestore.",
            "color": "indigo",
            "managed_by_google": [
                "ScaNN ANN vector index tree balancing & graph search (Partially Managed Storage)",
                "Dedicated GCE compute slice for low-latency vector similarity calculations",
            ],
            "customer_controls": [
                "Serving the search API (Customer Built): Customer must deploy and host the search serving API",
                "Text & metadata storage in Cloud Firestore (Partially Managed Storage)",
                "PDF document parsing & chunking pipeline (token size, overlap)",
                "Manual embedding generation pipeline (gemini-embedding-2 via API)",
                "Two-stage retrieval logic (ANN neighbor IDs -> Firestore document fetch)",
                "Manual prompt assembly & Gemini LLM synthesis",
            ],
            "tradeoffs": {
                "developer_effort": "High (~450 LOC pipeline, 2 separate storage systems to maintain)",
                "latency_profile": "Ultra-fast retrieval (<15ms), but requires extra network round-trip to Firestore",
                "cost_model": "Fixed hourly cost (Dedicated e2-standard-16 VM running 24/7 even with 0 queries)",
                "fine_grained_control": "Maximum (Full control over vector dimensions, index algorithms, and chunk schema)",
                "multitool_agentic": "Manual (Must be custom coded in the application layer)",
            },
            "golden_query_fit": {
                "Q1": "⭐⭐⭐⭐ High semantic relevance from embedding model",
                "Q2": "⭐⭐ Limited (Pure dense vector search struggles on exact form codes)",
                "Q3": "⭐⭐⭐ Depends on chunk boundary consistency during data prep",
                "Q4": "⭐ Unable to check employee balances without custom tool integration",
            } if corpus == "en" else {
                "Q1-ID": "⭐⭐⭐⭐ Relevansi semantik tinggi dari model embedding",
                "Q2-ID": "⭐⭐ Terbatas (Pencarian murni dense vector kurang sensitif terhadap kode PDN-402B)",
                "Q3-ID": "⭐⭐⭐ Bergantung pada kerapian chunking tabel pada saat prep data",
                "Q4-ID": "⭐ Tidak mampu mengecek saldo cuti karyawan tanpa integrasi tool manual",
            },
        },
        {
            "id": "s2",
            "name": "Agent Retrieval",
            "subtitle": "Serverless Collections + Hybrid Search",
            "badge": "Serverless Balance",
            "description": "Next-gen Vertex AI Vector Search featuring serverless collections, auto-embedding, and co-located DataObject payload storage.",
            "color": "emerald",
            "managed_by_google": [
                "Automated serverless embedding generation on DataObject creation in collection",
                "Zero-ops auto-scaling serverless collection infrastructure",
                "Co-located DataObject storage (Partially Managed Storage: serverless storage with customer-managed schema)",
            ],
            "customer_controls": [
                "Serving the search API (Customer Built): Serving means serving the search/agent; customer develops and hosts the API",
                "PDF document parsing & text chunking",
                "Structuring DataObject payload (text, doc_name, page, metadata)",
                "Final prompt construction and calling Gemini LLM",
            ],
            "tradeoffs": {
                "developer_effort": "Moderate (Eliminates Firestore and index endpoint deployment, ~250 LOC)",
                "latency_profile": "Fast (40-90ms), single API call returns chunks and payload directly",
                "cost_model": "Pay-per-operation (Billed only per query operation + GB stored)",
                "fine_grained_control": "High (Configurable hybrid alpha weight, flexible metadata filtering)",
                "multitool_agentic": "Moderate (Easily wrapped as a retrieval tool in agent frameworks)",
            },
            "golden_query_fit": {
                "Q1": "⭐⭐⭐⭐ Strong semantic match on parental leave policy",
                "Q2": "⭐⭐⭐⭐⭐ Excellent! Hybrid search (BM25) instantly locks onto 'EXP-402B'",
                "Q3": "⭐⭐⭐ Good, but multi-column tables may get split across chunk boundaries",
                "Q4": "⭐ Requires transactional agent logic to retrieve employee PTO balance",
            } if corpus == "en" else {
                "Q1-ID": "⭐⭐⭐⭐ Sangat baik dalam pencarian semantik konsep cuti",
                "Q2-ID": "⭐⭐⭐⭐⭐ Luar biasa! Hybrid search (BM25) langsung menangkap kode unik 'PDN-402B'",
                "Q3-ID": "⭐⭐⭐ Baik, namun struktur tabel kompleks dapat terpotong jika chunking tidak layout-aware",
                "Q4-ID": "⭐ Perlu logika agen tambahan untuk data saldo cuti personal",
            },
        },
        {
            "id": "s3",
            "name": "RAG Engine",
            "subtitle": "Managed File Corpus + Document Ingestion",
            "badge": "Enterprise RAG",
            "description": "Managed Vertex AI RAG Engine. Google orchestrates document parsing, chunking, embedding generation, and vector corpus storage directly from Cloud Storage.",
            "color": "blue",
            "managed_by_google": [
                "Direct automated document ingestion from Google Cloud Storage (GCS)",
                "Managed text chunking and document layout parsing",
                "Behind-the-scenes embedding generation on corpus import",
                "Unified managed RAG Corpus holding text passages, metadata, and vectors",
                "Managed context retrieval API (retrieve_contexts / rag.retrieval_query)",
            ],
            "customer_controls": [
                "Grounding & Answer Generation (Customer Built): RAG Engine is a retrieval-only service with NO generation capability; customer must construct prompt, call LLM, and build answer",
                "Serving the search API (Customer Built): Does not serve search directly; customer must build, deploy, and host the search serving API",
                "Chunk size and overlap configuration during Corpus initialization",
                "Embedding model selection at Corpus creation",
            ],
            "tradeoffs": {
                "developer_effort": "Low (~120 LOC, no need to write chunking/embedding pipeline)",
                "latency_profile": "Moderate (150-300ms for managed retrieval and custom LLM synthesis)",
                "cost_model": "Corpus storage per GB + managed RAG query API pricing + LLM generation tokens",
                "fine_grained_control": "Limited to initial chunk size, overlap parameters, and prompt design",
                "multitool_agentic": "High (Native VertexRagStore tool supported directly by Gemini)",
            },
            "golden_query_fit": {
                "Q1": "⭐⭐⭐⭐ High accuracy on parental leave policy lookups",
                "Q2": "⭐⭐⭐ Good, depending on embedding tokenization of form codes",
                "Q3": "⭐⭐⭐⭐ Clean layout parsing preserves table structure",
                "Q4": "⭐⭐ Explains remote work policy rules, but cannot access live employee data",
            } if corpus == "en" else {
                "Q1-ID": "⭐⭐⭐⭐ Sangat baik untuk pencarian kebijakan umum",
                "Q2-ID": "⭐⭐⭐ Cukup baik, tergantung representasi token kode di embedding",
                "Q3-ID": "⭐⭐⭐⭐ Chunking layout parser mengenali konteks tabel tunjangan dengan rapi",
                "Q4-ID": "⭐⭐ Mampu menjawab aturan kuota WFA, tetapi tidak tahu saldo sisa karyawan",
            },
        },
        {
            "id": "s4",
            "name": "Agent Search (Search API)",
            "subtitle": "Turnkey Enterprise Search & Grounded Answers",
            "badge": "Turnkey Search",
            "description": "Google Cloud Discovery Engine (Agent Search). End-to-end turnkey solution handling layout-aware PDF parsing, multi-index retrieval, cross-encoder reranking, and citation-grounded synthesis.",
            "color": "amber",
            "managed_by_google": [
                "Turnkey search & answer endpoint fully hosted by Google with global SLA and auto-scaling (Fully Managed Serving)",
                "Turnkey grounded summary generation with clickable citations and factual verification (Fully Managed Grounding & Generation)",
                "State-of-the-art layout-aware PDF parser (preserves tables and document hierarchy)",
                "Automatic hybrid dense + keyword search with deep cross-encoder reranking",
            ],
            "customer_controls": [
                "DataStore configuration and source PDF uploads to Cloud Storage",
                "SummarySpec configuration (number of results, language, citation style)",
                "Single API call to retrieve ranked results and an answer summary",
            ],
            "tradeoffs": {
                "developer_effort": "Very Low (~60 LOC for query execution and UI presentation)",
                "latency_profile": "Integrated (Single API call yields ranked search results + synthesized answer)",
                "cost_model": "Per-query enterprise pricing (Discovery Engine search pricing)",
                "fine_grained_control": "Low (Fully managed and auto-optimized by Google Cloud)",
                "multitool_agentic": "High (Native enterprise search connector for agent architectures)",
            },
            "golden_query_fit": {
                "Q1": "⭐⭐⭐⭐⭐ Direct citation and precise summary of 16-week paid parental leave",
                "Q2": "⭐⭐⭐⭐⭐ Flawlessly identifies Form EXP-402B > $500 and 30-day deadline",
                "Q3": "⭐⭐⭐⭐⭐ Multi-column table parsed into exact deductible and HSA comparisons",
                "Q4": "⭐⭐ Accurately explains 20 workday remote work limit, but lacks HRIS access",
            } if corpus == "en" else {
                "Q1-ID": "⭐⭐⭐⭐⭐ Sangat fasih dengan sitasi langsung ke dokumen Kebijakan Cuti",
                "Q2-ID": "⭐⭐⭐⭐⭐ Menemukan kode PDN-402B dan batas 14 hari dengan presisi sempurna",
                "Q3-ID": "⭐⭐⭐⭐⭐ Layout parser menjaga struktur tabel Staf vs Manajer secara akurat",
                "Q4-ID": "⭐⭐ Menjelaskan aturan WFA 20 hari secara akurat, namun tidak memiliki akses ke database saldo karyawan",
            },
        },
        {
            "id": "s5",
            "name": "Agent Search + Google ADK",
            "subtitle": "Active Reasoning Agent + Transactional Tools",
            "badge": "Agentic AI",
            "description": "Advanced cognitive agent built on Google Agent Development Kit (ADK). Combines policy retrieval via Agent Search with live transactional tool execution against enterprise HRIS.",
            "color": "purple",
            "managed_by_google": [
                "ReAct / Chain-of-Thought orchestration framework via Google ADK",
                "Gemini native function calling and structured tool execution loop",
                "Turnkey policy search via Discovery Engine DataStore tool",
            ],
            "customer_controls": [
                "Hosting agent runtime on Cloud Run with persistent session state (Partially Managed Serving)",
                "Custom business tool implementations (SQL database access, employee balances)",
                "Agent system instruction (reasoning policy, tone, error mitigation)",
                "Direct connection to internal enterprise systems (HRIS, ERP, Core Banking)",
            ],
            "tradeoffs": {
                "developer_effort": "Moderate (~180 LOC, focused on business logic and tool schemas)",
                "latency_profile": "Tiered (Scales with number of reasoning steps and tool round-trips)",
                "cost_model": "Multi-turn Gemini LLM tokens + Agent Search API calls",
                "fine_grained_control": "Maximum over reasoning flow, tool permissions, and business guardrails",
                "multitool_agentic": "Best-in-Class (Purpose-built for complex multi-step reasoning and actions)",
            },
            "golden_query_fit": {
                "Q1": "⭐⭐⭐⭐⭐ Details 16 weeks paid parental leave for primary caregivers",
                "Q2": "⭐⭐⭐⭐⭐ Identifies Form EXP-402B requirements and 30 calendar day window",
                "Q3": "⭐⭐⭐⭐⭐ Formats HDHP vs PPO comparison clearly",
                "Q4": "⭐⭐⭐⭐⭐ THE ONLY SCENARIO to solve Q4: Fetches Alex Johnson's EMP-1042 balance (14 PTO, 5 remote days used), confirms 15 days remote is within 20-day cap, and verifies 5 PTO days available!",
            } if corpus == "en" else {
                "Q1-ID": "⭐⭐⭐⭐⭐ Membaca aturan 5 hari cuti suami dan memberi panduan pengajuan",
                "Q2-ID": "⭐⭐⭐⭐⭐ Menjelaskan kegunaan form PDN-402B dan batas 14 hari kerja",
                "Q3-ID": "⭐⭐⭐⭐⭐ Menyajikan tabel komparasi plafon secara interaktif",
                "Q4-ID": "⭐⭐⭐⭐⭐ SATU-SATUNYA yang mampu memecahkan Q4-ID secara sempurna: Mengambil saldo riil EMP-1042 (7 cuti, 4 WFA), memverifikasi aturan 20 hari WFA, dan menghitung sisa kelayakan!",
            },
        },
    ]

    return {
        "scenarios": scenarios,
        "golden_queries": GOLDEN_QUERIES_EN if corpus == "en" else GOLDEN_QUERIES_ID,
        "golden_queries_id": GOLDEN_QUERIES_ID,
        "golden_queries_en": GOLDEN_QUERIES_EN,
        "documents": DOCUMENTS_EN if corpus == "en" else DOCUMENTS_ID,
        "documents_id": DOCUMENTS_ID,
        "documents_en": DOCUMENTS_EN,
        "document_count": len(DOCUMENTS_EN if corpus == "en" else DOCUMENTS_ID),
        "corpus": corpus,
    }


@app.get("/api/documents")
def get_documents_catalog(corpus: Optional[str] = "id"):
    docs = DOCUMENTS_EN if corpus == "en" else DOCUMENTS_ID
    return {
        "corpus": corpus,
        "count": len(docs),
        "documents": docs,
    }




# Serve Static Frontend Assets (Vite dist) jika sudah di-build
FRONTEND_DIST = PORTAL_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        target = FRONTEND_DIST / full_path
        if target.exists() and target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    def fallback_index():
        return {
            "title": "Cymbal HR FAQ Indonesia — Unified Gateway Server",
            "message": "Gateway backend is running. Frontend dist not yet built.",
            "routes": {
                "overview": "/api/overview",
                "health": "/api/health",
                "s1_health": "/api/s1/health",
                "s2_health": "/api/s2/health",
                "s3_health": "/api/s3/health",
                "s4_health": "/api/s4/health",
                "s5_health": "/api/s5/health",
                "api_docs": "/docs",
            },
        }


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
