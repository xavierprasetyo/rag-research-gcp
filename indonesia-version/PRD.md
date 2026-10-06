# PRD: Agen FAQ HR (Versi Indonesia) — Demo Perbandingan Arsitektur Retrieval & Search Google Cloud

**Penulis:** xavierprasetyo  
**Tanggal:** 2 Oktober 2026  
**Status:** Draf  
**Dokumen induk:** [global-version/PRD.md](../global-version/PRD.md) (versi bahasa Inggris)

---

## 1. Ringkasan

Dokumen ini mendefinisikan **versi Indonesia** dari demo Agen FAQ HR. Arsitektur kelima skenario **sama persis** dengan [global-version/PRD.md](../global-version/PRD.md); yang berbeda adalah **dataset, istilah, dan pertanyaan uji**, yang dilokalkan untuk konteks perusahaan di Indonesia (BPJS, THR, SPPD, cuti bersama, WFA, Rupiah).

Seperti versi bahasa Inggris, demo ini **tidak memeringkat** skenario. Tujuannya menunjukkan apa yang kita bangun sendiri, apa yang dikelola Google, dan apa yang kita korbankan di tiap skenario, kali ini untuk konten berbahasa Indonesia.

> [!NOTE]
> Versi Indonesia **bukan terjemahan** versi bahasa Inggris. Fakta, angka, dan nama dokumennya berbeda, jadi jawaban kedua demo tidak bisa dibandingkan satu per satu. Yang dibandingkan adalah **perilaku arsitekturnya**.

---

## 2. Konfigurasi Bahasa per Skenario

| Skenario | Konfigurasi untuk Bahasa Indonesia | Catatan |
| :--- | :--- | :--- |
| **1. Vector Search 1.0** | Embedding `gemini-embedding-2` (multibahasa), 768 dimensi, dipanggil di lokasi `global` | Prefiks dokumen `title: {judul} \| text: {isi}`, prefiks pertanyaan `task: question answering \| query: {pertanyaan}` |
| **2. Agent Retrieval** | Auto-embedding `gemini-embedding-2` pada collection `hr-faq-id` | Sudah diuji dan berfungsi di `us-central1` |
| **3. RAG Engine** | Embedding `text-multilingual-embedding-002` pada corpus `hr-faq-rag-id` | RAG Engine belum menerima model embedding Gemini. Model ini **pensiun 1 April 2027**. Sudah diuji dengan pertanyaan berbahasa Indonesia dan berfungsi. |
| **4. Agent Search API** | Data store `hr-faq-datastore-id`; `language_code="id"` pada permintaan ringkasan/jawaban | Bahasa Indonesia (`id-ID`) didukung resmi untuk pencarian, jawaban, dan pertanyaan lanjutan |
| **5. Agent Search + ADK** | Data store yang sama dengan Skenario 4; instruksi agen dalam Bahasa Indonesia | Nama fungsi tool tetap bahasa Inggris (konvensi kode) |

**LLM:** `gemini-3.8-flash` untuk semua skenario, dengan instruksi sistem: *"Jawab dalam Bahasa Indonesia yang baku dan ringkas. Sebutkan nama dokumen sumber."*

**Region:** `us-central1` (sama dengan versi bahasa Inggris).

---

## 3. Dataset: "Paket Kebijakan HR PT Cymbal Indonesia"

Empat dokumen PDF di folder `source-documents/`. Semua angka dan kebijakan **fiktif**, dirancang agar terasa realistis untuk perusahaan di Indonesia.

> [!WARNING]
> Kebijakan di bawah ini adalah data demo, **bukan nasihat hukum**. Minta tim HR/legal meninjau angka cuti dan tunjangan sebelum demo ditampilkan ke pelanggan, agar tidak bertentangan dengan peraturan ketenagakerjaan yang berlaku.

### 3.1 `01_Kebijakan_Cuti_Karyawan.pdf`

Teks naratif. Menguji **pencarian semantik**.

| Topik | Isi Kebijakan (Fiktif) |
| :--- | :--- |
| Cuti tahunan | 12 hari kerja setelah masa kerja 12 bulan; 15 hari setelah 5 tahun; 18 hari setelah 10 tahun |
| Cuti bersama | Mengikuti SKB pemerintah dan **memotong jatah cuti tahunan** |
| Sisa cuti | Maksimal 6 hari dapat dibawa ke tahun berikutnya; hangus jika tidak dipakai sebelum 31 Maret |
| Cuti melahirkan | 3 bulan berbayar penuh |
| Cuti pendampingan persalinan (untuk suami) | 5 hari kerja berbayar penuh, diambil dalam 30 hari setelah kelahiran |
| Cuti duka | 3 hari kerja (keluarga inti); 1 hari (anggota keluarga serumah) |
| Cuti besar | 1 bulan setelah masa kerja 6 tahun berturut-turut |

### 3.2 `02_Panduan_Tunjangan_dan_Kesehatan_2026.pdf`

Berisi **tabel multikolom**. Menguji **parsing tabel**.

- **BPJS Kesehatan** dan **BPJS Ketenagakerjaan** (JHT, JKK, JKM, JP) untuk semua karyawan tetap.
- **Asuransi kesehatan tambahan** dengan plafon per level jabatan:

| Manfaat | Staf | Supervisor | Manajer | Direktur |
| :--- | :--- | :--- | :--- | :--- |
| Rawat inap (kamar per hari) | Rp750.000 | Rp1.000.000 | Rp1.500.000 | Rp2.500.000 |
| Rawat jalan (per tahun) | Rp5.000.000 | Rp7.500.000 | Rp12.000.000 | Rp20.000.000 |
| Persalinan normal | Rp8.000.000 | Rp10.000.000 | Rp15.000.000 | Rp20.000.000 |
| Persalinan caesar | Rp15.000.000 | Rp20.000.000 | Rp30.000.000 | Rp40.000.000 |
| Kacamata (per 2 tahun) | Rp1.000.000 | Rp1.500.000 | Rp2.000.000 | Rp3.000.000 |

- **THR:** 1 kali gaji pokok + tunjangan tetap, dibayar paling lambat H-7 Idulfitri (pro-rata untuk masa kerja di bawah 12 bulan).

### 3.3 `03_Kebijakan_Perjalanan_Dinas_dan_Reimburse.pdf`

Berisi **kode formulir, singkatan, dan ambang batas**. Menguji **pencarian kata kunci**.

| Topik | Isi Kebijakan (Fiktif) |
| :--- | :--- |
| SPPD | Setiap perjalanan dinas wajib memiliki **Surat Perintah Perjalanan Dinas (SPPD)** yang disetujui atasan langsung |
| Formulir **PDN-402B** | Formulir pertanggungjawaban biaya perjalanan dinas; diajukan **paling lambat 14 hari kalender** setelah SPPD selesai, beserta kuitansi asli |
| Uang harian | Wilayah I (Jakarta, Surabaya, Bali): Rp600.000/hari; Wilayah II (ibu kota provinsi lain): Rp450.000/hari; Wilayah III (lainnya): Rp350.000/hari |
| Persetujuan | Reimburse di atas Rp5.000.000 memerlukan persetujuan VP |
| Kuitansi | Pengeluaran di atas Rp250.000 wajib disertai kuitansi atau faktur pajak |

### 3.4 `04_FAQ_WFH_WFA_dan_Tunjangan_Peralatan.pdf`

Format tanya-jawab dengan **campuran istilah Indonesia–Inggris** yang umum di kantor (WFH, WFA, reimburse).

| Topik | Isi Kebijakan (Fiktif) |
| :--- | :--- |
| WFH | Maksimal 2 hari per minggu, dengan persetujuan atasan langsung |
| WFA dalam negeri | Maksimal **20 hari kerja per tahun**; pengajuan paling lambat 7 hari sebelumnya |
| WFA luar negeri | Hanya dengan persetujuan Direktur dan tim Keamanan TI; maksimal 10 hari kerja per tahun |
| Tunjangan peralatan kerja | Rp10.000.000 setiap 3 tahun (kursi, meja, monitor) |
| Tunjangan internet | Rp300.000 per bulan bagi karyawan yang WFH minimal 1 hari per minggu |
| Laptop | Laptop inventaris kantor wajib memakai VPN saat WFA |

---

## 4. Pertanyaan Uji (Golden Queries)

Keempat pertanyaan meniru *pola uji* versi bahasa Inggris, tetapi dengan konteks lokal.

| ID | Pertanyaan Pengguna | Trade-off yang Diperlihatkan |
| :--- | :--- | :--- |
| **Q1-ID (Semantik)** | *"Istri saya baru saja melahirkan. Saya dapat libur berapa hari?"* | Pertanyaan memakai kata sehari-hari ("istri melahirkan", "libur"), sedangkan dokumen memakai istilah formal **"cuti pendampingan persalinan"**. Semua skenario seharusnya bisa menjembatani ini lewat kemiripan semantik, sehingga yang terlihat adalah perbedaan **usaha developer dan latensi**. |
| **Q2-ID (Kode & Singkatan)** | *"Formulir PDN-402B itu untuk apa, dan berapa lama batas pengajuannya setelah SPPD selesai?"* | Kode formulir (`PDN-402B`) dan singkatan (`SPPD`) adalah kasus klasik pencarian kata kunci. Membandingkan **hybrid search** di Skenario 4–5 dan Skenario 2 dengan **dense vector murni** di Skenario 1. |
| **Q3-ID (Tabel)** | *"Bandingkan plafon rawat jalan per tahun dan tunjangan persalinan caesar antara level Staf dan Manajer."* | Jawabannya ada di sel tabel multikolom. Membandingkan **parsing tabel terkelola** (Skenario 3 dengan Layout Parser, Skenario 4) dengan ekstraksi teks `pypdf` biasa (Skenario 1–2). |
| **Q4-ID (Agentik + Tool HR)** | *"Saya karyawan EMP-1042. Boleh nggak saya WFA dari Bali 15 hari kerja bulan depan, dan sisa cuti tahunan saya cukup nggak untuk ambil 5 hari cuti tambahan di sana?"* | Hanya **Skenario 5** yang bisa menjawab kedua bagian: mencari aturan WFA lewat `VertexAiSearchTool` **dan** memanggil tool `get_employee_leave_balance("EMP-1042")`. Bahasanya sengaja informal ("boleh nggak", "cukup nggak") dan bercampur istilah Inggris ("WFA"). |

---

## 5. Hal Khusus Bahasa Indonesia yang Perlu Diperhatikan

Poin-poin ini menambah trade-off yang tidak terlihat di versi bahasa Inggris:

1. **Pilihan model embedding di RAG Engine lebih sempit.** Untuk bahasa Indonesia, RAG Engine hanya bisa memakai `text-multilingual-embedding-002` (rilis 2024, pensiun April 2027). Skenario 1–2 bisa memakai `gemini-embedding-2` yang lebih baru.
2. **Imbuhan bahasa Indonesia** (misalnya *ajukan / mengajukan / pengajuan*) bisa memengaruhi pencarian kata kunci. Agent Search mendukung `id-ID` secara resmi. Untuk `TextSearch` di Agent Retrieval, penanganan imbuhan bahasa Indonesia **belum diverifikasi**, jadi periksa saat implementasi.
3. **Campur kode Indonesia–Inggris** ("reimburse", "WFA", "plafon rawat jalan") umum di dokumen HR. Model embedding multibahasa umumnya menangani ini, tetapi pencarian kata kunci murni bisa meleset jika pengguna menulis "penggantian biaya" sementara dokumen menulis "reimburse".
4. **Gaya bahasa informal** ("nggak", "dapat libur") berbeda jauh dari bahasa dokumen yang baku. Ini menguji kekuatan semantik tiap skenario.

---

## 6. Sumber Daya dan Penamaan

| Skenario | Nama Sumber Daya |
| :--- | :--- |
| 1. Vector Search 1.0 | Index `hr-faq-index-id` (+ penyimpanan teks chunk); bisa di-deploy ke endpoint yang sama dengan versi bahasa Inggris |
| 2. Agent Retrieval | Collection `hr-faq-id` |
| 3. RAG Engine | Corpus `hr-faq-rag-id` |
| 4–5. Agent Search | Data store `hr-faq-datastore-id` + engine terkait |
| Dokumen sumber | `gs://my-bucket/hr-docs/id/` |

### Tool HR untuk Skenario 5

```python
def get_employee_leave_balance(employee_id: str) -> dict:
    """Mengambil sisa cuti tahunan dan jumlah hari WFA yang sudah terpakai dari sistem HRIS."""
    return HRIS_DB[employee_id]  # contoh: {"sisa_cuti_tahunan": 7, "hari_wfa_terpakai": 4}

hr_agent_id = Agent(
    name="cymbal_hr_agent_id",
    model="gemini-3.8-flash",
    instruction=(
        "Kamu adalah asisten HR PT Cymbal Indonesia. Gunakan Agent Search untuk mencari kebijakan HR resmi, "
        "dan panggil get_employee_leave_balance jika karyawan bertanya tentang sisa cuti atau kuota WFA miliknya. "
        "Jawab dalam Bahasa Indonesia yang baku dan ringkas."
    ),
    tools=[
        VertexAiSearchTool(data_store_id=DATA_STORE_PATH["id"], bypass_multi_tools_limit=True),
        get_employee_leave_balance,
    ],
)
```

---

## 7. Daftar Istilah

| Istilah | Arti |
| :--- | :--- |
| **BPJS Kesehatan** | Jaminan kesehatan nasional |
| **BPJS Ketenagakerjaan** | Jaminan sosial tenaga kerja (JHT, JKK, JKM, JP) |
| **THR** | Tunjangan Hari Raya |
| **Cuti bersama** | Cuti yang ditetapkan pemerintah di sekitar hari libur nasional |
| **SPPD** | Surat Perintah Perjalanan Dinas |
| **Uang harian** | Tunjangan harian selama perjalanan dinas |
| **Plafon** | Batas maksimal penggantian biaya |
| **WFH / WFA** | *Work from home* / *work from anywhere* |
| **Reimburse** | Penggantian biaya yang sudah dikeluarkan karyawan |

---

## 8. Single Unified Portal & Gateway Architecture

Untuk mempermudah demonstrasi dan evaluasi komparatif, seluruh skenario disajikan melalui **Single Unified Portal** di folder [unified-portal/](unified-portal/):
- **Frontend Terpadu:** React + Vite + Tailwind CSS dengan **Home Page** (visualisasi arsitektur 5 skenario, *Google Managed vs Customer Controlled*, matriks trade-off, dan panduan golden query) serta **5 Halaman Menu Skenario**.
- **FastAPI Gateway (Port 8000):** Me-mount router non-overlapping dari tiap folder skenario (`01` s/d `05`) di bawah prefix `/api/s1` s/d `/api/s5`.
- **Independensi Backend:** Masing-masing folder skenario tetap memiliki komponen logika, evaluasi CLI (`eval_golden.py`), dan otomasi sumber daya sendiri.

Spesifikasi lengkap dan arsitektur terinci ada di [unified-portal/PRD.md](unified-portal/PRD.md).

