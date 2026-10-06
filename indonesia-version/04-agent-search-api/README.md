# Skenario 4: Agent Search (Search & Answer API) — Versi Indonesia

Turnkey retrieval & answer generation menggunakan **Google Cloud Discovery Engine** (Agent Search).

## Karakteristik Arsitektur
- **Layanan:** Google Cloud Discovery Engine
- **DataStore ID:** `hr-faq-datastore-id`
- **Search Engine ID:** `hr-faq-search-id`
- **Location:** `global`
- **Tanggung Jawab Google:**
  - Parsing layout PDF dokumen bahasa Indonesia secara otomatis (teks narasi, list, dan tabel).
  - Chunking adaptif berbasis semantik dan struktur.
  - Hybrid Search (dense vector embedding + BM25 keyword index).
  - Cross-encoder reranking.
  - Turnkey summarization dengan sitasi berakar langsung dalam Bahasa Indonesia (`language_code="id"`).
- **Tanggung Jawab Klien:**
  - Mengunggah file PDF sumber ke Cloud Storage (`gs://rag-research-sandbox-hr-docs/hr-docs/id/`).
  - Memanggil `SearchServiceClient.search()` dengan query pengguna.

## Menjalankan Skenario Mandiri
```bash
# 1. Cek status DataStore & Engine di GCP
python manage_datastore.py status

# 2. Inisialisasi DataStore, Engine, dan impor dokumen dari GCS
python manage_datastore.py create

# 3. Jalankan server backend (port 8004)
./spinup.sh

# 4. Jalankan evaluasi Golden Queries (Q1-ID s/d Q4-ID)
python eval_golden.py
```
