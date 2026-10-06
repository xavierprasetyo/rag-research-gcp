# Agen FAQ HR — Versi Indonesia

Asisten FAQ HR yang sama, dibangun dengan lima cara di Google Cloud, untuk memperlihatkan trade-off antara kendali penuh dan kemudahan layanan terkelola. Demo ini tidak memeringkat skenario. Desain lengkap ada di [PRD.md](PRD.md).

Dataset versi ini **dilokalkan** untuk perusahaan di Indonesia (BPJS, THR, SPPD, cuti bersama, WFA, Rupiah), bukan terjemahan versi global. Versi bahasa Inggris ada di [../global-version](../global-version/README.md).

## Struktur Folder

| Folder | Skenario | Yang Kita Bangun vs. yang Dikelola Google |
| :--- | :--- | :--- |
| [01-vector-search-1.0](01-vector-search-1.0/) | Vector Search (1.0) | Kita membangun parsing, chunking, embedding, penyimpanan teks chunk, dan prompt; Google menyediakan index ANN dan endpoint |
| [02-agent-retrieval](02-agent-retrieval/) | Agent Retrieval (sebelumnya Vector Search 2.0) | Kita membangun parsing, chunking, dan prompt; Google menyimpan data + vektor dan membuat embedding otomatis |
| [03-rag-engine](03-rag-engine/) | RAG Engine | Kita mengatur corpus dan memanggil Gemini; Google melakukan parsing, chunking, embedding, dan penyimpanan |
| [04-agent-search-api](04-agent-search-api/) | Agent Search: Search & Answer API | Kita cukup satu panggilan API; Google menjalankan seluruh pipeline dan menyusun jawaban |
| [05-agent-search-adk](05-agent-search-adk/) | Agent Search + Agen ADK | Kita membangun agen dan tool HR; Google mengelola data store dan retrieval |
| [source-documents](source-documents/) | Dataset bersama | 4 PDF "Paket Kebijakan HR PT Cymbal Indonesia" yang dipakai semua skenario |

## Konfigurasi Bersama

| Pengaturan | Nilai |
| :--- | :--- |
| LLM | `gemini-3.8-flash`, menjawab dalam Bahasa Indonesia |
| Embedding | `gemini-embedding-2` (Skenario 1–2), `text-multilingual-embedding-002` (Skenario 3), dikelola Agent Search (Skenario 4–5) |
| Region | `us-central1` |
| Akhiran nama sumber daya | `-id` |

## Pertanyaan Uji

| ID | Pertanyaan | Pola |
| :--- | :--- | :--- |
| Q1-ID | Istri saya baru saja melahirkan. Saya dapat libur berapa hari? | Semantik |
| Q2-ID | Formulir PDN-402B itu untuk apa, dan berapa lama batas pengajuannya setelah SPPD selesai? | Kode & singkatan |
| Q3-ID | Bandingkan plafon rawat jalan per tahun dan tunjangan persalinan caesar antara level Staf dan Manajer. | Tabel |
| Q4-ID | Saya karyawan EMP-1042. Boleh nggak saya WFA dari Bali 15 hari kerja bulan depan, dan sisa cuti tahunan saya cukup nggak untuk ambil 5 hari cuti tambahan di sana? | Agentik + tool HR |

## Unified Portal & Cloud Run Deployment

Seluruh 5 skenario terintegrasi ke dalam **Single Unified Portal** (React 19 + Tailwind v4 + FastAPI Gateway):
- **Live Cloud Run URL:** [https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app](https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app)
- **API Health Check:** [https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app/api/health](https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app/api/health)
- **API Swagger Docs:** [https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app/docs](https://cymbal-hr-unified-portal-1031440951381.us-central1.run.app/docs)

### Menjalankan secara Lokal
```bash
cd /home/admin_xavierprasetyo_altostrat_c/learn/vector-search-gcp/indonesia-version
./spinup.sh          # Menjalankan Unified Gateway & Portal di http://localhost:8000
./spinup.sh 4        # Menjalankan Skenario 4 standalone di http://localhost:8004
./spinup.sh 5        # Menjalankan Skenario 5 standalone di http://localhost:8005
./teardown.sh        # Menghentikan seluruh proses
```

## Status

Semua 5 skenario (Skenario 1 s/d 5) dan Single Unified Portal telah selesai dibangun, terverifikasi 100% pada evaluasi Golden Queries (Q1-ID s/d Q4-ID), dan terdeploy di Google Cloud Run.
