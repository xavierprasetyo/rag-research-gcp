# Unified Portal — Cymbal HR FAQ Indonesia (5 Arsitektur Google Cloud)

Portal antarmuka terpadu (Single Unified UI & Gateway) yang menggabungkan seluruh 5 skenario arsitektur pencarian dan pengambilan data di Google Cloud ke dalam satu pengalaman interaktif:
1. **Skenario 1:** Vector Search 1.0 (Dedicated ANN Index + Firestore)
2. **Skenario 2:** Agent Retrieval (Serverless Collections + Hybrid Search)
3. **Skenario 3:** RAG Engine (Managed RagCorpus + Ingestion)
4. **Skenario 4:** Agent Search (Turnkey Discovery Engine Search & Answer API)
5. **Skenario 5:** Agent Search + Google ADK (Active Multi-Tool Reasoning Agent)

## Fitur Utama Portal
- **Beranda (Showcase & Trade-off):**
  - Diagram visual perbandingan alur pemrosesan data (Pipeline Visualizer).
  - Label pemisahan transparan: **Google Managed** vs. **Customer Built/Controlled**.
  - Matriks trade-off lengkap: Usaha Developer (LOC), Latensi, Biaya, Fleksibilitas Kontrol, dan Dukungan Agen.
  - Panduan kecocokan Golden Query (Q1-ID s/d Q4-ID).
  - Status live resource GCP untuk tiap skenario.
- **5 Menu Skenario Mandiri:**
  - Selector cepat Golden Query (Bahasa Indonesia).
  - Breakdown kartu latensi (Retrieval, Generasi LLM, Total ms).
  - Penampil fragmen dokumen (Chunks / Snippets) dan sitasi resmi.
- **Rich Agent Execution Inspector (Skenario 5):**
  - Simulator identitas karyawan HRIS (`EMP-1042`, `EMP-2088`, `EMP-3001`).
  - Rekaman jejak penalaran berjenjang (*Thought -> Tool Call 1: HRIS -> Tool Call 2: Policy -> Final Answer*).

## Menjalankan Portal Terpadu
```bash
# 1. Jalankan gateway server (port 8000)
./spinup.sh

# 2. Buka di browser
http://localhost:8000
```
