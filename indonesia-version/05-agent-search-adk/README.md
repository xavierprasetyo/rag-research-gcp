# Skenario 5: Agent Search + Google ADK — Versi Indonesia

Asisten HR cerdas bertenaga **Google Agent Development Kit (`google-adk`)** yang mampu melakukan penalaran multi-step (*Chain-of-Thought*), pencarian regulasi perusahaan via Discovery Engine / Agent Search, serta pemanggilan data transaksional langsung dari database HRIS.

## Karakteristik Arsitektur
- **Framework Agen:** Google ADK (`from google.adk import Agent, Runner`)
- **LLM:** `gemini-2.5-flash`
- **Tools:**
  1. `search_company_policy(query)`: Retrieval kebijakan resmi dari DataStore `hr-faq-datastore-id`.
  2. `get_employee_leave_balance(employee_id)`: Mengambil sisa cuti tahunan, pemakaian WFA, level jabatan, dan divisi langsung dari database HRIS.
- **Tanggung Jawab:**
  - Agen secara otonom menentukan tool mana yang dipanggil berdasarkan isi pertanyaan.
  - Untuk pertanyaan hibrida (Q4-ID), agen memanggil kedua alat secara berurutan, melakukan kalkulasi matematika sisa kuota, dan menyajikan ringkasan solutif.

## Menjalankan Skenario Mandiri
```bash
# 1. Jalankan server backend (port 8005)
./spinup.sh

# 2. Jalankan evaluasi Golden Queries (Q1-ID s/d Q4-ID)
python eval_golden.py
```
