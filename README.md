# Enterprise Generative Search & RAG Architectures on Google Cloud

A comprehensive, end-to-end benchmark and interactive portal comparing five generative search and Retrieval-Augmented Generation (RAG) architectural patterns on Google Cloud Platform (GCP).

🌐 **Live Deployed Portal (Cloud Run):** [https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app](https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app)

---

## 🏗️ The 5 Architectural Scenarios

| Scenario | Core GCP Technology | Architectural Paradigm | Ingestion | Retrieval & Grounding | Serving |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S1: Vector Search 1.0** | Vertex AI Vector Search (Dedicated ScaNN Index) + Cloud Firestore | Custom DIY Infrastructure | Customer Built (PyPDF + chunker + manual embeddings) | Customer Built (ANN vector lookup + Firestore text fetch + Gemini LLM) | Customer Built (Dedicated VM nodes + custom API) |
| **S2: Agent Retrieval** | Vertex AI Vector Search (Serverless Collections) | Serverless Vector Store | Customer Built (Push JSON DataObjects, auto-embedded by collection) | Partially Managed (Serverless dense search + custom LLM synthesis) | Customer Built (Customer hosts search/agent serving API) |
| **S3: RAG Engine** | Vertex AI RAG Engine (`vertexai.preview.rag`) | Managed Document Corpus | Google Managed (Direct GCS sync + Layout Parser + auto-embedding) | Partially Managed Retrieval + Customer Built Generation (Retrieval-only) | Customer Built (Customer hosts search/agent serving API) |
| **S4: Agent Search API** | Google Cloud Discovery Engine | Turnkey Enterprise Search | Google Managed (DocAI OCR, table layout chunking, multi-crawlers) | Google Managed (Hybrid dense + BM25, cross-encoder, grounded summary) | Google Managed (Turnkey endpoint with global SLA) |
| **S5: Agent ADK** | Google Agent Development Kit (ADK) + Gemini Function Calling | Autonomous Cognitive Agent | Google Managed (Enterprise DataStore + live operational SQL DB) | Google Managed (ReAct reasoning loop, tool execution, math checks) | Partially Managed (Cloud Run agent runtime with session state) |

---

## 📐 Steps of a Modern Generative Search (Canonical Blueprint)

Every modern enterprise search system follows a 10-step lifecycle, cleanly separated into **Preparation (Data Ingestion)** and **Runtime (Data Retrieval & Serving)**:

### 1. Preparation • Data Ingestion Pipeline
1. **Connect to your data**: Ingesting raw documents, database records, and streaming enterprise feeds into the pipeline.
2. **Parsing / Understanding**: Extracting clean text, structural layouts, tables, and media representations from raw formats.
3. **Chunking**: Segmenting content into coherent semantic passages while preserving context and metadata.
4. **Embedding**: Transforming textual passages into dense numerical vectors capturing semantic meaning.
5. **Storage**: Persisting dense vector indexes, chunk text payloads, and relational metadata for retrieval.

### 2. Runtime • Data Retrieval & Serving Pipeline
6. **Query Expansion & Understanding**: Analyzing user intent, correcting spelling, expanding synonyms, and rewriting search queries.
7. **Search & Relevance**: Matching user queries against stored data via dense semantic similarity and keyword algorithms.
8. **Ranking & Optimization**: Re-ordering candidate results by relevance scoring, freshness, user signals, and business KPIs.
9. **Grounding, Answer & Conversation**: Synthesizing retrieved contexts into natural language answers with citations and multi-turn state.
10. **Serving**: Serving the search endpoint or agent runtime with secure authentication, low latency, and scale.

### 🎨 Responsibility Taxonomy
- 🟢 **Google Managed**: Platform handles 100% of operational and algorithmic complexity.
- 🟡 **Partially Managed**: Shared responsibility (e.g. platform manages index while customer manages payload database, or hybrid data stores).
- 🟣 **Customer Built**: Customer developers must design, write code, deploy, and maintain.

---

## ⚖️ Critical Architectural Distinctions

1. **Serving & Storage in Vector Search (S1 & S2):**
   - **Serving means serving the search or agent API.** In Vector Search, serving is **NOT managed** (customer built and hosted).
   - Only **storage is partially managed** (Google manages vector index traversal, while document text and metadata are stored in external customer databases or co-managed DataObjects).
2. **RAG Engine vs. Agent Search API (S3 vs. S4):**
   - **RAG Engine is a retrieval-only service.** It has **no generation capabilities** out-of-the-box. Customers must construct system prompts, invoke an LLM (such as Gemini), assemble citations, and build their own serving endpoint.
   - **Agent Search API is turnkey.** It natively generates citation-grounded answer summaries and provides a fully hosted, scalable search endpoint with Google global SLA.
3. **Autonomous Reasoning with Agent ADK (S5):**
   - S1 through S4 can only answer questions based on static policy documents.
   - S5 combines policy retrieval with real-time enterprise database tools (e.g. querying employee leave balances, validating PTO requests, and performing policy math).

---

## 📚 10 Master Enterprise Policies & Bilingual Corpus

The repository includes a 10-document enterprise HR policy suite in both **Indonesian** and **Global English**:

| # | Indonesian Policy File | Global English Policy File | Document Code | Domain |
| :---: | :--- | :--- | :--- | :--- |
| **01** | `01_Kebijakan_Cuti_Karyawan.pdf` | `01_Global_PTO_and_Leave_Policy.pdf` | `HC-KBJ-001/2026` | Annual Leave, Paternity & Maternity |
| **02** | `02_Panduan_Tunjangan_dan_Kesehatan_2026.pdf` | `02_2026_Benefits_and_Healthcare_Guide.pdf` | `HC-PND-002/2026` | Health Insurance, Outpatient Plafond |
| **03** | `03_Kebijakan_Perjalanan_Dinas_dan_Reimburse.pdf` | `03_Expense_and_Travel_Reimbursement_Policy.pdf` | `HC-KBJ-003/2026` | Travel Per Diems, Expense Deadlines |
| **04** | `04_FAQ_WFH_WFA_dan_Tunjangan_Peralatan.pdf` | `04_Remote_Work_and_Equipment_Stipend_FAQ.pdf` | `HC-FAQ-004/2026` | Work From Anywhere (WFA), Hardware |
| **05** | `05_Kebijakan_Kompensasi_Lembur_dan_THR.pdf` | `05_Global_Compensation_Overtime_and_Bonus_Plan.pdf` | `HC-KBJ-005/2026` | Overtime Formulas, Prorated Bonuses |
| **06** | `06_Kode_Etik_Anti_Korupsi_dan_Whistleblowing.pdf` | `06_Global_Code_of_Conduct_Anti_Corruption_and_Whistleblowing.pdf` | `HC-KBJ-006/2026` | Anti-Bribery, Gift Reporting Limits |
| **07** | `07_Panduan_Manajemen_Kinerja_dan_Promosi.pdf` | `07_Performance_Calibration_Promotion_and_PIP_Guidelines.pdf` | `HC-PND-007/2026` | Performance Calibration, PIP Durations |
| **08** | `08_Kebijakan_Keamanan_Informasi_BYOD_dan_Privasi_Data.pdf` | `08_Information_Security_BYOD_and_Acceptable_Use_Policy.pdf` | `HC-KBJ-008/2026` | InfoSec, MDM, BYOD Data Privacy |
| **09** | `09_Program_Pengembangan_Karyawan_dan_Beasiswa.pdf` | `09_Learning_Development_and_Tuition_Assistance_Program.pdf` | `HC-KBJ-009/2026` | Tuition Reimbursement, Certifications |
| **10** | `10_Prosedur_Terminasi_Resignasi_dan_Pesangon.pdf` | `10_Offboarding_Severance_and_Separation_Policy.pdf` | `HC-SOP-010/2026` | Separation SOP, Severance Multipliers |

---

## 📂 Repository Structure

```tree
vector-search-gcp/
├── indonesia-version/
│   ├── 01-vector-search-1.0/      # Scenario 1: Dedicated ScaNN Index + Firestore
│   ├── 02-agent-retrieval/        # Scenario 2: Serverless Collections + Hybrid
│   ├── 03-rag-engine/             # Scenario 3: Vertex AI Managed RAG Corpus
│   ├── 04-agent-search-api/       # Scenario 4: Google Cloud Discovery Engine
│   ├── 05-agent-search-adk/       # Scenario 5: Cognitive Agent via Google ADK
│   ├── source-documents/          # 10 Indonesian PDF Master Documents
│   ├── source-documents-en/       # 10 English PDF Master Documents
│   ├── shared_corpus_metadata.py  # Centralized document & golden query metadata
│   ├── unified-portal/            # Full-stack Portal (FastAPI backend + React frontend)
│   │   ├── frontend/              # TailwindCSS + Lucide + Vite interactive UI
│   │   └── server.py              # Unified API Gateway aggregating all 5 scenarios
│   └── Dockerfile                 # Multi-stage container for Cloud Run deployment
├── global-version/                # Initial baseline standalone notebooks & scripts
├── sync_all_scenarios_expanded.py # Master sync & evaluation pipeline for 10 policies
├── GEMINI.md                      # Architecture notes & project memory
└── README.md
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Google Cloud SDK (`gcloud`) authenticated with a GCP project

### 1. Setup Backend
```bash
cd indonesia-version
python -m venv .venv
source .venv/bin/activate
pip install -r unified-portal/requirements.txt
```

### 2. Build Frontend
```bash
cd indonesia-version/unified-portal/frontend
npm install
npm run build
```

### 3. Start Gateway Server
```bash
cd indonesia-version/unified-portal
python server.py
# Portal runs at http://localhost:8080
```

---

## ☁️ Deploying to Cloud Run

```bash
# 1. Build and push container to Artifact Registry
gcloud builds submit \
  --tag=us-central1-docker.pkg.dev/${PROJECT_ID}/cymbal-hr-repo/cymbal-hr-unified-portal:latest \
  indonesia-version/

# 2. Deploy service
gcloud run deploy cymbal-hr-unified-portal \
  --image=us-central1-docker.pkg.dev/${PROJECT_ID}/cymbal-hr-repo/cymbal-hr-unified-portal:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated
```

---

## 📄 License
This repository is licensed under the Apache 2.0 License.
