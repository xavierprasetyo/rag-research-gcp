# Skenario 3: RAG Engine — Versi Indonesia

Pipeline RAG terkelola: arahkan corpus ke GCS, lalu Google melakukan parsing, chunking, embedding, dan penyimpanan. Kita hanya mengatur corpus dan memanggil Gemini. Lihat [PRD global, Skenario 3](../../global-version/PRD.md#scenario-3-vertex-ai-rag-engine-ragcorpus).

| Item | Nilai |
| :--- | :--- |
| Sumber daya | RagCorpus `hr-faq-rag-id`, sumber `gs://rag-research-sandbox-hr-docs/hr-docs/id/` |
| Embedding | `text-multilingual-embedding-002` (tetap selama umur corpus; pensiun 1 April 2027) |
| Chunking | `chunk_size=512`, `chunk_overlap=100` (dikelola RAG Engine) |
| LLM | `gemini-3.5-flash-lite` (lokasi `global`), instruksi Bahasa Indonesia |
| Kita bangun | Konfigurasi corpus, panggilan Gemini dengan tool retrieval |
| Trade-off | Kode pipeline minimal; model embedding Gemini belum diizinkan, dan endpoint harus satu region dengan corpus |

## Dua Cara Memakai Corpus yang Sama

| Mode | Cara kerja | Latensi |
| :--- | :--- | :--- |
| `tool` (default) | `VertexRagStore` dipasang sebagai tool di `generate_content`; Google mengambil chunk dan Gemini menjawab dalam satu panggilan | Hanya total (retrieval ada di dalam panggilan Gemini) |
| `retrieve` | Kita panggil `rag.retrieval_query`, susun prompt sendiri seperti Skenario 1–2 | Retrieval dan generasi terpisah; jarak vektor chunk terlihat |

## Berkas

| Berkas | Fungsi |
| :--- | :--- |
| [config.py](config.py) | Project, corpus, embedding, chunking, dan golden queries |
| [manage_corpus.py](manage_corpus.py) | `create` (bucket, unggah PDF, corpus, `import_files`), `status`, `delete [--bucket]` |
| [retriever.py](retriever.py) | `RagEngineRetriever` dengan mode `tool` dan `retrieve` |
| [eval_golden.py](eval_golden.py) | Benchmark Q1-ID s/d Q4-ID di kedua mode, hasil ke `eval_results.json` |
| [server.py](server.py) | FastAPI (`/api/query`, `/api/health`, `/api/golden-queries`, `/api/benchmark`) + React build |
| [frontend/](frontend/) | UI React + Vite: kartu golden query, pemilih mode, inspector chunk, tabel benchmark |

## Cara Menjalankan

```bash
./spinup.sh              # buat bucket + corpus + import jika belum ada (~3 menit), lalu jalankan UI di http://localhost:8000
./teardown.sh            # hentikan server, hapus corpus dan bucket (tidak ada biaya tersisa)
./teardown.sh --keep     # hentikan server saja; corpus dan bucket tetap ada
```

Perintah manual (dari folder ini, dengan virtualenv root repository):

```bash
../../.venv/bin/python manage_corpus.py create|status|delete [--bucket]
../../.venv/bin/python eval_golden.py
```

Mengubah UI: `cd frontend && npm run dev` (port 3000, proxy `/api` ke 8000), lalu `npm run build`.

## Catatan Penyiapan (ditemukan saat implementasi, 6 Oktober 2026)

1. **Mode Serverless wajib.** Project baru ditolak membuat corpus mode Spanner di `us-central1`. `manage_corpus.py` mengalihkan RAG Engine ke Serverless lewat `aiplatform_v1beta1` (SDK `vertexai.rag` belum mengeksposnya). Ini pengaturan tingkat project.
2. **IAM.** Corpus Serverless dibuat di atas Vector Search Collection, sehingga service agent RAG (`service-1031440951381@gcp-sa-vertex-rag.iam.gserviceaccount.com`) butuh `roles/vectorsearch.admin` di project. Peran ini sudah diberikan di `rag-research-sandbox`.
3. **`vertexai.rag` sudah deprecated** (diarahkan ke klien `agentplatform`), tetapi masih berfungsi dan dipakai di PRD.
4. **Parser default, bukan Layout Parser.** Import memakai parser bawaan. Layout Parser (Document AI) belum dikonfigurasi, jadi klaim parsing tabel terkelola di PRD untuk Q3-ID baru diuji dengan parser bawaan.
5. **Skor `retrieve` adalah jarak**, bukan kemiripan: makin kecil makin relevan.

## Hasil Uji Golden Queries

Lihat [eval_results.json](eval_results.json). Pada 6 Oktober 2026, keempat pertanyaan mengembalikan dokumen yang benar di top-4 pada kedua mode (8 dari 8). Total latensi sekitar 2–3,8 detik; di mode `retrieve`, retrieval (~1,5–2,7 detik) lebih lambat daripada generasi (~1,1–1,3 detik). Q4-ID di skenario ini hanya menguji pencarian aturan WFA, bukan pemanggilan tool HR (itu Skenario 5).

## Pembersihan

`./teardown.sh` menghapus corpus dan bucket. Yang sengaja dibiarkan karena tidak ditagih: mode Serverless RAG Engine dan peran `roles/vectorsearch.admin`. Untuk mencabut peran tersebut:

```bash
gcloud projects remove-iam-policy-binding rag-research-sandbox \
  --member="serviceAccount:service-1031440951381@gcp-sa-vertex-rag.iam.gserviceaccount.com" \
  --role=roles/vectorsearch.admin
```
