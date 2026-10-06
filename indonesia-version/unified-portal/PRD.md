# PRD: Unified Portal & Scenarios 4 & 5 (Indonesia Version)
## Perbandingan Arsitektur Retrieval & Search Google Cloud

**Penulis:** Antigravity & Tim Cloud Architecture  
**Tanggal:** 6 Oktober 2026  
**Status:** Approved by Alignment Interview  
**Dokumen Induk:** [../PRD.md](../PRD.md)  

---

## 1. Ringkasan Eksekutif & Tujuan

Proyek ini melengkapi demonstrasi 5 Arsitektur Retrieval & Search di Google Cloud untuk versi Indonesia dengan:
1. **Mengimplementasikan Skenario 4 (`04-agent-search-api`):** Turnkey Search & Answer API menggunakan Discovery Engine (Agent Search) dengan pemahaman tata letak dokumen (layout parser), hybrid search, dan ringkasan berakar sitasi otomatis dalam Bahasa Indonesia.
2. **Mengimplementasikan Skenario 5 (`05-agent-search-adk`):** Agen cerdas bertenaga Google ADK (`Agent`) yang menggabungkan retrieval kebijakan via `VertexAiSearchTool` dan pemanggilan data transaksional langsung via custom tool HRIS (`get_employee_leave_balance`).
3. **Membangun Single Unified UI & Gateway Portal (`unified-portal`):** Satu antarmuka web terpadu dengan:
   - **Halaman Beranda (Home Page):** Menampilkan visualisasi arsitektur 5 skenario, pemisahan tegas tanggung jawab (*What Google Manages vs. What Customer Controls*), matriks trade-off komprehensif, serta panduan kecocokan Golden Query.
   - **5 Menu Khusus Skenario:** Masing-masing skenario memiliki halaman interaktif lengkap dengan parameter uji, query golden, inspeksi chunk/sitasi, serta rincian latensi.
   - **Rich Agent Execution Inspector (Skenario 5):** Menampilkan jejak penalaran multi-step (*Thought -> Tool Calls -> Observation -> Grounded Synthesis*) beserta simulator profil karyawan HRIS.
4. **Mempertahankan Komponen Backend Mandiri (Non-Overlapping):** Setiap folder skenario (`01`–`05`) tetap modular, memiliki konfigurasi, retriever, router FastAPI, skrip manajemen sumber daya (`manage_*.py`), skrip evaluasi CLI (`eval_golden.py`), dan `spinup.sh` sendiri. Gateway server di portal utama me-mount router-router ini di bawah prefix bersih (`/api/s1` s/d `/api/s5`).

---

## 2. Arsitektur Solusi & Tanggung Jawab

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SINGLE UNIFIED PORTAL (Port 8000)                     │
│  React + Vite + Tailwind CSS + Lucide Icons                                 │
│  [ Home: Tradeoff Showcase ] [ S1 ] [ S2 ] [ S3 ] [ S4 ] [ S5: ADK Agent ]  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / JSON
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GATEWAY SERVER (server.py)                            │
│  FastAPI Gateway mounted on port 8000 (Serves UI + Unified APIs)            │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│   /api/s1   │   /api/s2   │   /api/s3   │   /api/s4   │       /api/s5       │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │             │                 │
       ▼             ▼             ▼             ▼                 ▼
 ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      ┌──────────┐
 │Scenario 1│  │Scenario 2│  │Scenario 3│  │Scenario 4│      │Scenario 5│
 │  Vector  │  │  Agent   │  │   RAG    │  │  Agent   │      │Agent ADK │
 │Search 1.0│  │Retrieval │  │  Engine  │  │Search API│      │ + Search │
 └──────────┘  └──────────┘  └──────────┘  └──────────┘      └──────────┘
```

### Pemisahan Tanggung Jawab Komponen Backend
| Skenario | Folder | Modul Router | Retriever / Agent | CLI Management | CLI Eval |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S1: Vector Search 1.0** | `01-vector-search-1.0` | `router.py` | `VS1Retriever` (`retriever.py`) | `manage_index.py` | `eval_golden.py` |
| **S2: Agent Retrieval** | `02-agent-retrieval` | `router.py` | `AgentRetriever` (`retriever.py`) | `manage_collection.py` | `eval_golden.py` |
| **S3: RAG Engine** | `03-rag-engine` | `router.py` | `RagEngineRetriever` (`retriever.py`) | `manage_corpus.py` | `eval_golden.py` |
| **S4: Agent Search API** | `04-agent-search-api` | `router.py` | `AgentSearchRetriever` (`retriever.py`) | `manage_datastore.py` | `eval_golden.py` |
| **S5: Agent Search + ADK** | `05-agent-search-adk` | `router.py` | `ADKHRAgent` (`agent.py`) | Memakai DataStore S4 | `eval_golden.py` |

---

## 3. Spesifikasi Skenario 4: Agent Search (Search & Answer API)

### 3.1 Gambaran Umum
Menggunakan layanan terkelola **Google Cloud Discovery Engine** (Agent Search) untuk melakukan pencarian enterprise siap pakai. Google mengelola parsing layout dokumen PDF (tabel, teks naratif), chunking adaptif, dense vector + BM25 keyword hybrid search, reranking dengan cross-encoder, dan sintesis ringkasan jawaban dengan sitasi berakar.

### 3.2 Sumber Daya GCP
- **Project ID:** `rag-research-sandbox`
- **Location:** `global` (untuk Discovery Engine API)
- **Data Store ID:** `hr-faq-datastore-id`
- **Search Engine ID:** `hr-faq-search-id`
- **Sumber Data:** Dokumen PDF Indonesia di `gs://rag-research-sandbox-hr-docs/hr-docs/id/`
- **Parsing Config:** Digital layout / OCR parser terkelola
- **Summary Spec:** `summary_result_count=4`, `include_citations=True`, `language_code="id"`

### 3.3 Komponen File
- `config.py`: Definisi konstanta GCP, Data Store ID, Engine ID, dan Golden Queries.
- `manage_datastore.py`: Skrip otomasi untuk membuat/memeriksa data store, engine, dan memicu ingesti dokumen dari GCS.
- `retriever.py`: Wrapper `discoveryengine.SearchServiceClient` mengeksekusi pencarian berakar sitasi.
- `router.py`: FastAPI `APIRouter` mengekspos `/api/s4/query`, `/api/s4/health`, `/api/s4/documents`.
- `eval_golden.py`: Skrip evaluasi CLI menguji Q1-ID hingga Q4-ID.
- `spinup.sh` & `teardown.sh`: Otomasi peluncuran dan pembersihan mandiri.

---

## 4. Spesifikasi Skenario 5: Agent Search + Google ADK

### 4.1 Gambaran Umum
Mengimplementasikan asisten HR berbasis penalaran aktif menggunakan **Google Agent Development Kit (`google-adk`)**. Agen tidak sekadar membaca dokumen pasif, melainkan mampu menalar apakah pertanyaan membutuhkan:
1. Aturan kebijakan umum (retrieval dari Agent Search via `VertexAiSearchTool`), dan/atau
2. Data pribadi/transaksional karyawan secara langsung (memanggil Python tool `get_employee_leave_balance`).

### 4.2 Skema Tool & Mock HRIS
```python
HRIS_DB = {
    "EMP-1042": {
        "nama": "Budi Santoso",
        "jabatan": "Staf Operasional",
        "sisa_cuti_tahunan": 7,
        "hari_wfa_terpakai": 4,
        "lokasi_kantor": "Jakarta",
    },
    "EMP-2088": {
        "nama": "Siti Rahma",
        "jabatan": "Supervisor Keuangan",
        "sisa_cuti_tahunan": 14,
        "hari_wfa_terpakai": 18,
        "lokasi_kantor": "Surabaya",
    },
    "EMP-3001": {
        "nama": "Ahmad Fauzi",
        "jabatan": "Manajer Teknik",
        "sisa_cuti_tahunan": 3,
        "hari_wfa_terpakai": 20,
        "lokasi_kantor": "Jakarta",
    },
}
```

### 4.3 Spesifikasi Penanganan Q4-ID
Pertanyaan: *"Saya karyawan EMP-1042. Boleh nggak saya WFA dari Bali 15 hari kerja bulan depan, dan sisa cuti tahunan saya cukup nggak untuk ambil 5 hari cuti tambahan di sana?"*
- **Langkah 1:** Agen mengenali ID karyawan `EMP-1042` dan memanggil `get_employee_leave_balance("EMP-1042")` $\rightarrow$ mendapati sisa cuti 7 hari, WFA terpakai 4 hari dari kuota tahunan.
- **Langkah 2:** Agen memanggil `VertexAiSearchTool` mencari aturan WFA di dokumen `04_FAQ_WFH_WFA_dan_Tunjangan_Peralatan.pdf` $\rightarrow$ mendapati batas WFA dalam negeri adalah 20 hari kerja/tahun dengan pengajuan H-7.
- **Langkah 3 (Penalaran):**
  - Kuota WFA tersisa: $20 - 4 = 16$ hari kerja. Pengajuan 15 hari diperbolehkan ($15 \le 16$).
  - Sisa cuti tahunan: 7 hari. Tambahan cuti 5 hari mencukupi ($5 \le 7$).
  - Syarat tambahan: Mengajukan minimal 7 hari kerja sebelumnya (H-7).
- **Langkah 4:** Agen merangkum jawaban lugas, empatik, dan berdasar data riil.

### 4.4 Komponen File
- `config.py`: Definisi model LLM, prompt sistem agen, dataset mock HRIS.
- `agent.py`: Inisialisasi ADK `Agent`, tool binding, dan runner dengan trace capture.
- `router.py`: FastAPI `APIRouter` mengekspos `/api/s5/query`, `/api/s5/employees`, `/api/s5/health`.
- `eval_golden.py`: Evaluasi CLI menguji eksekusi multi-step dan akurasi logika Q4-ID.
- `spinup.sh` & `teardown.sh`: Otomasi mandiri.

---

## 5. Spesifikasi Unified Portal & Antarmuka UI

### 5.1 Tata Letak Navigasi
Aplikasi web modern (Single Page App) dengan navigasi bilah samping/atas:
1. **🏠 Beranda: Showcase & Trade-off**
2. **1️⃣ S1: Vector Search 1.0 (Dedicated ANN + Firestore)**
3. **2️⃣ S2: Agent Retrieval (Serverless Collections)**
4. **3️⃣ S3: RAG Engine (Managed File Corpus)**
5. **4️⃣ S4: Agent Search (Turnkey Search & Answer API)**
6. **5️⃣ S5: Agent ADK (Search + Transactional Tools)**

### 5.2 Fitur Halaman Beranda
1. **Visual Pipeline Diagram:** Flow diagram interaktif membandingkan alur data dari file PDF mentah ke parsing $\rightarrow$ chunking $\rightarrow$ embedding $\rightarrow$ indexing $\rightarrow$ retrieval $\rightarrow$ prompt $\rightarrow$ LLM generation.
2. **Pemisahan Tanggung Jawab (*Google Managed* vs *Customer Built*):** Penandaan visual dengan warna kontras (misal: Indigo untuk kode yang kita bangun, Emerald untuk layanan yang dikelola otomatis oleh Google).
3. **Matriks Perbandingan Komprehensif:**
   - Usaha developer (Lines of Code)
   - Karakteristik latensi & performa
   - Model biaya (Dedicated VM vs. Serverless Query)
   - Fleksibilitas & kontrol internal
   - Dukungan tabel multikolom & semantik
4. **Panduan Golden Query (Q1-ID s/d Q4-ID):** Menjelaskan keunggulan dan keterbatasan tiap skenario terhadap 4 pola pertanyaan uji.
5. **GCP Resource Live Status:** Badges status waktu-nyata untuk setiap skenario yang terhubung ke backend.

### 5.3 Fitur Halaman Skenario (1–5)
- Tombol uji cepat Golden Queries (Q1–Q4) sekali klik.
- Kolom pertanyaan bebas dengan auto-focus.
- Kartu indikator latensi terperinci (Waktu retrieval, generasi, dan total).
- Kontainer jawaban yang rapi dengan format Markdown & sitasi.
- Panel penampil potongan teks (*chunk/data object/search result viewer*) lengkap dengan metadata, nomor halaman, dan skor relevansi/jarak.
- Khusus Skenario 5: **Rich Agent Execution Inspector** menampilkan panel reasoning step-by-step (*Thought process, tool inputs, tool outputs, synthesis*) dan panel pemilih profil karyawan HRIS.

---

## 6. Jadwal & Rencana Pelaksanaan

1. **Fase 1:** Implementasi Modul Skenario 4 (`04-agent-search-api`) lengkap dengan config, manage_datastore, retriever, router, eval, spinup.
2. **Fase 2:** Implementasi Modul Skenario 5 (`05-agent-search-adk`) lengkap dengan config, agent ADK, HR tools, router, eval, spinup.
3. **Fase 3:** Refactoring router di Skenario 1, 2, 3 agar bersih dan siap di-mount oleh Gateway.
4. **Fase 4:** Pembangunan `unified-portal` (FastAPI Gateway `server.py` dan Vite + React Frontend terintegrasi).
5. **Fase 5:** Skrip orkestrasi induk `indonesia-version/spinup.sh` dan pengujian verifikasi menyeluruh (non-long-lived verification).
