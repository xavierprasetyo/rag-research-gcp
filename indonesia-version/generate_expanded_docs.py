#!/usr/bin/env python3
"""
generate_expanded_docs.py — Generates 6 new enterprise-grade HR policy PDFs in Indonesian
and 6 matching global HR policy PDFs in English (Topics 5 through 10).

Each document is structured as a multi-page corporate standard PDF with metadata boxes,
structured sections, multi-column data tables, bold formula codes, and legal disclaimers.
"""

import shutil
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

BASE_DIR = Path(__file__).resolve().parent
ID_DOCS_DIR = BASE_DIR / "source-documents"
EN_DOCS_DIR = BASE_DIR / "source-documents-en"
GLOBAL_DOCS_DIR = BASE_DIR.parent / "global-version" / "source-documents"

ID_DOCS_DIR.mkdir(parents=True, exist_ok=True)
EN_DOCS_DIR.mkdir(parents=True, exist_ok=True)
GLOBAL_DOCS_DIR.mkdir(parents=True, exist_ok=True)


def build_styles():
    base = getSampleStyleSheet()
    
    org_header = ParagraphStyle(
        "OrgHeader",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
        textTransform="uppercase",
        spaceAfter=3,
    )
    
    doc_title = ParagraphStyle(
        "DocTitle",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    
    meta_bar = ParagraphStyle(
        "MetaBar",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
        spaceAfter=14,
    )
    
    h2 = ParagraphStyle(
        "Heading2_Custom",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=4,
    )
    
    body = ParagraphStyle(
        "Body_Custom",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )
    
    bullet = ParagraphStyle(
        "Bullet_Custom",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4,
    )
    
    tbl_header = ParagraphStyle(
        "TblHeader",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=0,
    )
    
    tbl_cell = ParagraphStyle(
        "TblCell",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
        alignment=0,
    )
    
    tbl_cell_bold = ParagraphStyle(
        "TblCellBold",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
    )
    
    callout = ParagraphStyle(
        "Callout",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=4,
        spaceAfter=6,
    )
    
    disclaimer = ParagraphStyle(
        "Disclaimer",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748b"),
        spaceBefore=14,
    )

    return {
        "org_header": org_header,
        "doc_title": doc_title,
        "meta_bar": meta_bar,
        "h2": h2,
        "body": body,
        "bullet": bullet,
        "tbl_header": tbl_header,
        "tbl_cell": tbl_cell,
        "tbl_cell_bold": tbl_cell_bold,
        "callout": callout,
        "disclaimer": disclaimer,
    }


def create_pdf(filename: Path, elements: list):
    doc = SimpleDocTemplate(
        str(filename),
        pagesize=letter,
        leftMargin=48,
        rightMargin=48,
        topMargin=46,
        bottomMargin=46,
    )
    doc.build(elements)
    print(f"✓ Generated PDF: {filename.name} ({filename.stat().st_size:,} bytes)")


def style_table(headers, rows, col_widths, styles):
    table_data = []
    header_row = [Paragraph(h, styles["tbl_header"]) for h in headers]
    table_data.append(header_row)
    
    for row in rows:
        formatted_row = []
        for i, val in enumerate(row):
            s = styles["tbl_cell_bold"] if i == 0 else styles["tbl_cell"]
            formatted_row.append(Paragraph(str(val), s))
        table_data.append(formatted_row)
        
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ])
    )
    return t


# ==============================================================================
# INDONESIAN DOCUMENTS (05 to 10)
# ==============================================================================

def generate_id_doc_05(styles):
    target = ID_DOCS_DIR / "05_Kebijakan_Kompensasi_Lembur_dan_THR.pdf"
    e = []
    e.append(Paragraph("PT CYMBAL INDONESIA · DIVISI HUMAN CAPITAL & REMUNERASI", styles["org_header"]))
    e.append(Paragraph("Kebijakan Kompensasi, Upah Lembur, dan Tunjangan Hari Raya (THR)", styles["doc_title"]))
    e.append(Paragraph("Nomor: HC-KBJ-015/2026 · Revisi 2 · Berlaku sejak 1 Januari 2026 · Pemilik: Divisi Kompensasi & Benefit", styles["meta_bar"]))
    
    e.append(Paragraph("1. Tujuan dan Ruang Lingkup", styles["h2"]))
    e.append(Paragraph("Kebijakan ini menetapkan pedoman baku terkait struktur kompensasi, formula upah kerja lembur, tunjangan kehadiran, serta pembayaran Tunjangan Hari Raya (THR) Keagamaan bagi seluruh karyawan PT Cymbal Indonesia sesuai Peraturan Pemerintah (PP) No. 35 Tahun 2021 dan peraturan ketenagakerjaan Republik Indonesia yang berlaku.", styles["body"]))
    
    e.append(Paragraph("2. Struktur Kompensasi dan Grading", styles["h2"]))
    e.append(Paragraph("Penghasilan bulanan karyawan terdiri atas Gaji Pokok, Tunjangan Tetap (tunjangan jabatan), dan Tunjangan Tidak Tetap (tunjangan makan dan transportasi). Level kepangkatan dibagi ke dalam grading L1 hingga L8. Karyawan berstatus Non-Exempt (L1 hingga L4) berhak atas upah lembur resmi, sedangkan level Manajer ke atas (L5 ke atas) berstatus Exempt yang kompensasinya sudah mencakup beban tanggung jawab kepemimpinan.", styles["body"]))
    
    e.append(Paragraph("3. Ketentuan dan Perhitungan Upah Kerja Lembur (Overtime)", styles["h2"]))
    e.append(Paragraph("Waktu kerja normal adalah 40 jam per minggu (8 jam per hari untuk 5 hari kerja). Lembur hanya diperkenankan atas penugasan atasan dengan batas maksimal 4 jam per hari dan 18 jam per minggu (di luar lembur hari libur resmi).", styles["body"]))
    e.append(Paragraph("Dasar perhitungan upah lembur mengacu pada formula resmi ketenagakerjaan: <b>Upah Sejam = 1/173 × (Gaji Pokok + Tunjangan Tetap)</b>.", styles["callout"]))
    
    headers = ["Kategori Lembur", "Rincian Jam Kerja", "Faktor Pengali", "Contoh Perhitungan"]
    rows = [
        ["Hari Kerja Biasa", "Jam Pertama (Jam ke-1)", "1,5 × Upah Sejam", "1,5 × (1/173 × Gaji Pokok)"],
        ["Hari Kerja Biasa", "Jam Kedua dan seterusnya", "2,0 × Upah Sejam", "2,0 × (1/173 × Gaji Pokok)"],
        ["Hari Libur Resmi / Weekend", "Jam ke-1 s.d. Jam ke-7", "2,0 × Upah Sejam", "2,0 × (1/173 × Gaji Pokok) per jam"],
        ["Hari Libur Resmi / Weekend", "Jam ke-8", "3,0 × Upah Sejam", "3,0 × (1/173 × Gaji Pokok)"],
        ["Hari Libur Resmi / Weekend", "Jam ke-9 dan Jam ke-10", "4,0 × Upah Sejam", "4,0 × (1/173 × Gaji Pokok) per jam"],
    ]
    e.append(style_table(headers, rows, [110, 130, 110, 160], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("4. Prosedur Administrasi Lembur (Surat Perintah Kerja Lembur - Form OT-201)", styles["h2"]))
    e.append(Paragraph("Pengajuan lembur wajib didahului Formulir Perintah Kerja Lembur (<b>Form OT-201</b>) yang disetujui Manajer minimal H-1 sebelum pelaksanaan. Untuk kejadian darurat operasional (incident support), formulir dapat diajukan secara retrospektif maksimal H+2 hari kerja. Karyawan yang lembur minimal 3 jam berturut-turut berhak atas uang saku makan lembur sebesar <b>Rp 45.000,-</b> per hari.", styles["body"]))
    
    e.append(PageBreak())
    e.append(Paragraph("5. Tunjangan Hari Raya (THR) Keagamaan", styles["h2"]))
    e.append(Paragraph("Sesuai Permenaker No. 6 Tahun 2016, perusahaan wajib membayarkan THR Keagamaan kepada seluruh karyawan yang mempunyai masa kerja minimal 1 (satu) bulan secara terus menerus paling lambat <b>H-7 (tujuh hari) sebelum Hari Raya Keagamaan</b>.", styles["body"]))
    
    thr_headers = ["Masa Kerja Karyawan", "Besaran Nominal THR Keagamaan", "Ketentuan Khusus"]
    thr_rows = [
        ["Masa Kerja ≥ 12 Bulan", "1 (Satu) Bulan Upah Penuh (Gaji Pokok + Tunjangan Tetap)", "Dibayarkan 100% tanpa potongan"],
        ["Masa Kerja 1 s.d. < 12 Bulan", "Prorata: (Masa Kerja dalam Bulan / 12) × Upah Sebulan", "Dihitung bulanan penuh pembulatan"],
        ["Resign Sebelum H-30 Hari Raya", "Tidak Berhak Memperoleh THR", "Berlaku bagi karyawan PKWTT"],
        ["PKWT Berakhir Sebelum Hari Raya", "Tidak Berhak Memperoleh THR", "Kecuali kontrak diperpanjang sebelum H-7"],
    ]
    e.append(style_table(thr_headers, thr_rows, [140, 200, 170], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("6. Bonus Tahunan Berbasis Kinerja (Annual KPI Bonus)", styles["h2"]))
    e.append(Paragraph("Bonus tahunan dialokasikan berdasarkan pencapaian laba operasional perusahaan dan penilaian kinerja individu (rating akhir tahun). Pembayaran bonus dilakukan bersamaan dengan slip gaji bulan Maret.", styles["body"]))
    e.append(Paragraph("• <b>Rating 5 (Outstanding):</b> Pengali bonus 2,50 × Gaji Pokok.", styles["bullet"]))
    e.append(Paragraph("• <b>Rating 4 (Exceeds Expectations):</b> Pengali bonus 1,75 × Gaji Pokok.", styles["bullet"]))
    e.append(Paragraph("• <b>Rating 3 (Meets Expectations):</b> Pengali bonus 1,00 × Gaji Pokok.", styles["bullet"]))
    e.append(Paragraph("• <b>Rating 1 - 2 (Needs Improvement):</b> Tidak berhak memperoleh bonus tahunan.", styles["bullet"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("PT Cymbal Indonesia adalah perusahaan fiktif. Dokumen ini adalah data demo untuk pengujian sistem Generative Search / RAG dan bukan nasihat hukum ketenagakerjaan.", styles["disclaimer"]))
    create_pdf(target, e)


def generate_id_doc_06(styles):
    target = ID_DOCS_DIR / "06_Kode_Etik_Anti_Korupsi_dan_Whistleblowing.pdf"
    e = []
    e.append(Paragraph("PT CYMBAL INDONESIA · DIVISI LEGAL, KEPATUHAN & TATA KELOLA", styles["org_header"]))
    e.append(Paragraph("Kode Etik Bisnis, Anti-Gratifikasi, dan Saluran Pelaporan Pelanggaran", styles["doc_title"]))
    e.append(Paragraph("Nomor: LC-KBJ-004/2026 · Revisi 4 · Berlaku sejak 1 Januari 2026 · Pemilik: Tim Kepatuhan Korporat & Etika", styles["meta_bar"]))
    
    e.append(Paragraph("1. Prinsip Integritas dan Nilai Utama", styles["h2"]))
    e.append(Paragraph("PT Cymbal Indonesia berkomitmen menerapkan standar etika tertinggi, transparansi tata kelola, dan kepatuhan mutlak terhadap hukum tindak pidana korupsi di Indonesia. Seluruh pimpinan dan karyawan wajib menjunjung tinggi nilai kejujuran, keadilan perlakuan, dan perlindungan aset pemangku kepentingan.", styles["body"]))
    
    e.append(Paragraph("2. Kebijakan Anti-Suap, Anti-Korupsi, dan Batasan Hadiah Bisnis", styles["h2"]))
    e.append(Paragraph("Karyawan dilarang keras meminta, menerima, menjanjikan, atau memberikan suap, uang pelicin (grease payment), kickback, atau bentuk kompensasi terselubung apapun kepada pihak swasta, mitra bisnis, maupun Pejabat Penyelenggara Negara (ASN/BUMN).", styles["body"]))
    
    headers = ["Kategori Pemberian / Hadiah", "Ambang Batas Nilai Maksimal", "Kewajiban Pelaporan", "Tindakan Disetujui"]
    rows = [
        ["Hadiah Souvenir / Parsel Vendor", "Maksimal Rp 500.000,- per vendor/tahun", "Wajib lapor Form ETH-101 ≤ 3 hari", "Dapat diterima jika bernilai wajar"],
        ["Hadiah Uang Tunai / Voucher / Logam Mulia", "Rp 0,- (DILARANG KERAS)", "Wajib tolak dan lapor segera", "Penolakan langsung seketika"],
        ["Jamuan Makan Bisnis (Business Meal)", "Maksimal Rp 750.000,- per orang", "Dicatat dalam klaim expense manajer", "Pertemuan diskusi bisnis formal"],
        ["Hadiah kepada Penyelenggara Negara", "Rp 0,- (NOL RUPIAH)", "Wajib tolak & eskalasi Tim Legal", "Kategori tindak pidana suap/gratifikasi"],
    ]
    e.append(style_table(headers, rows, [140, 130, 120, 120], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("3. Pelaporan Gratifikasi dan Formulir ETH-101", styles["h2"]))
    e.append(Paragraph("Apabila dalam kondisi tertentu hadiah tidak dapat ditolak (misalnya dikirimkan ke rumah/kantor tanpa pemberitahuan sebelumnya), penerima wajib mengisi <b>Formulir Pelaporan Hadiah & Gratifikasi (Form ETH-101)</b> ke Unit Kepatuhan dalam waktu paling lambat <b>3 (tiga) hari kerja</b>. Komite Etik berhak memutuskan apakah hadiah tersebut diserahkan kepada yayasan sosial perusahaan atau diundi untuk seluruh staf pada kegiatan akhir tahun.", styles["body"]))
    
    e.append(PageBreak())
    e.append(Paragraph("4. Benturan Kepentingan (Conflict of Interest) dan Form COI-202", styles["h2"]))
    e.append(Paragraph("Benturan kepentingan timbul apabila kepentingan pribadi, finansial, atau relasi keluarga karyawan memengaruhi objektivitas keputusan profesionalnya di Cymbal. Ketentuan baku:", styles["body"]))
    e.append(Paragraph("• <b>Afiliasi Vendor / Bisnis Sampingan:</b> Karyawan dilarang memiliki kepemilikan saham > 1% atau menjadi pengurus pada perusahaan vendor, mitra, atau kompetitor aktif Cymbal.", styles["bullet"]))
    e.append(Paragraph("• <b>Hubungan Keluarga:</b> Karyawan yang memiliki hubungan suami/istri, orang tua, anak, atau saudara kandung dilarang berada dalam satu garis hierarki pengawasan langsung.", styles["bullet"]))
    e.append(Paragraph("• <b>Deklarasi Tahunan:</b> Seluruh karyawan wajib melengkapi Deklarasi Benturan Kepentingan (<b>Form COI-202</b>) setiap bulan Januari melalui portal kepatuhan internal.", styles["bullet"]))
    
    e.append(Paragraph("5. Sistem Pengaduan Pelanggaran Independen (Whistleblowing System)", styles["h2"]))
    e.append(Paragraph("Cymbal menyediakan kanal pelaporan rahasia dan independen untuk melaporkan dugaan kecurangan, fraud, korupsi, pelecehan, pelanggaran keselamatan kerja, atau pelanggaran hukum lainnya:", styles["body"]))
    
    wbs_headers = ["Kanal Whistleblower", "Alamat Kontak / Akses", "Waktu Layanan & Keamanan"]
    wbs_rows = [
        ["Email Pengaduan Khusus", "etika@cymbal.co.id", "Terkoneksi langsung ke Auditor Utama & Tim Legal"],
        ["Hotline Bebas Pulsa", "0800-1-CYMBAL (0800-1-296225)", "Senin - Jumat, 08.00 - 18.00 WIB (Operator Independen)"],
        ["Portal Pelaporan Aman", "https://whistleblower.cymbal.co.id", "Tersedia 24/7 dengan opsi pelapor 100% anonim"],
        ["Surat Fisik Tertutup", "PO BOX 1042 JKT KEPATUHAN", "Amplop bersegel ditujukan kepada Ketua Komite Etik"],
    ]
    e.append(style_table(wbs_headers, wbs_rows, [130, 180, 200], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("6. Jaminan Perlindungan Pelapor (Anti-Retaliation Policy)", styles["h2"]))
    e.append(Paragraph("Perusahaan menjamin kerahasiaan identitas pelapor dan memberikan perlindungan hukum mutlak dari segala bentuk tindakan balasan (retaliation), diskriminasi, penurunan peringkat, pemotongan kompensasi, mutasi paksa, maupun pemecatan sepihak. Setiap pimpinan atau rekan kerja yang terbukti melakukan intimidasi terhadap pelapor akan dikenakan sanksi Pemutusan Hubungan Kerja (PHK) berat tanpa pesangon serta dilaporkan ke pihak kepolisian sesuai UU Perlindungan Saksi dan Korban.", styles["body"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("PT Cymbal Indonesia adalah perusahaan fiktif. Dokumen ini adalah data demo untuk pengujian sistem Generative Search / RAG dan bukan nasihat hukum ketenagakerjaan.", styles["disclaimer"]))
    create_pdf(target, e)


def generate_id_doc_07(styles):
    target = ID_DOCS_DIR / "07_Panduan_Manajemen_Kinerja_dan_Promosi.pdf"
    e = []
    e.append(Paragraph("PT CYMBAL INDONESIA · DIVISI TALENT & ORGANIZATION DEVELOPMENT", styles["org_header"]))
    e.append(Paragraph("Panduan Manajemen Kinerja, Matriks Kenaikan Gaji, Promosi, dan PIP", styles["doc_title"]))
    e.append(Paragraph("Nomor: HC-PDN-008/2026 · Revisi 3 · Berlaku sejak 1 Januari 2026 · Pemilik: Divisi Manajemen Kinerja & Talenta", styles["meta_bar"]))
    
    e.append(Paragraph("1. Prinsip dan Siklus Manajemen Kinerja", styles["h2"]))
    e.append(Paragraph("Manajemen kinerja di PT Cymbal Indonesia berorientasi pada pencapaian sasaran strategis perusahaan melalui metodologi Objectives & Key Results (OKR). Siklus evaluasi diselenggarakan dalam tiga tahapan berkala:", styles["body"]))
    e.append(Paragraph("• <b>Januari:</b> Penetapan sasaran tahunan (Goal Setting & OKR Alignment).", styles["bullet"]))
    e.append(Paragraph("• <b>Juni - Juli:</b> Mid-Year Check-in (kajian formatif kemajuan proyek tanpa penilaian angka kuantitatif).", styles["bullet"]))
    e.append(Paragraph("• <b>November - Desember:</b> Year-End Performance Evaluation & Cross-Departmental Calibration.", styles["bullet"]))
    
    e.append(Paragraph("2. Skala Penilaian Kinerja Karyawan (Rating Scale 1–5)", styles["h2"]))
    headers = ["Rating", "Sebutan Predikat", "Definisi Pencapaian Kinerja", "Panduan Distribusi"]
    rows = [
        ["5", "Outstanding (Sangat Istimewa)", "Secara konsisten melampaui seluruh target strategis (>125%), dampak luas korporasi", "Maksimal 10%"],
        ["4", "Exceeds Expectations (Melebihi Target)", "Mencapai seluruh target dan melampaui sasaran utama (110% - 124%), kinerja proaktif", "Target ~25%"],
        ["3", "Meets Expectations (Memenuhi Standar)", "Kinerja solid dan konsisten mencapai target yang disepakati (90% - 109%)", "Target ~55%"],
        ["2", "Needs Improvement (Perlu Perbaikan)", "Kinerja di bawah ekspektasi pada area kompetensi utama (70% - 89%), butuh supervisi", "Target ~8%"],
        ["1", "Unsatisfactory (Tidak Memuaskan)", "Gagal mencapai target minimum mendasar (<70%), dampak negatif pada tim", "Target ~2%"],
    ]
    e.append(style_table(headers, rows, [45, 145, 230, 90], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("3. Matriks Kenaikan Gaji Tahunan (Merit Increase Matrix)", styles["h2"]))
    e.append(Paragraph("Kenaikan gaji berkala (merit increase) dihitung berdasarkan rating kinerja individu dan posisi gaji karyawan terhadap titik tengah pasar (compa-ratio). Kenaikan gaji efektif berlaku per tanggal 1 Maret tahun berjalan.", styles["body"]))
    
    merit_headers = ["Rating Akhir Tahun", "Persentase Kenaikan Gaji (Merit)", "Kelayakan Bonus KPI", "Tindakan Pengembangan"]
    merit_rows = [
        ["Rating 5", "10,0% s.d. 15,0%", "Dapat Bonus Penuh × 2,5", "Kandidat Jalur Akselerasi Talenta (HiPo)"],
        ["Rating 4", "7,0% s.d. 9,9%", "Dapat Bonus Penuh × 1,75", "Disiapkan untuk Peluang Promosi / Lead"],
        ["Rating 3", "3,5% s.d. 6,9%", "Dapat Bonus Normal × 1,0", "Pengembangan Kompetensi Lanjutan"],
        ["Rating 2", "0,0% (Tidak Ada Kenaikan)", "Tidak Berhak Bonus", "Evaluasi Bimbingan Khusus 3 Bulan"],
        ["Rating 1", "0,0% (Tidak Ada Kenaikan)", "Tidak Berhak Bonus", "Wajib Masuk Program PIP 60 Hari"],
    ]
    e.append(style_table(merit_headers, merit_rows, [80, 130, 130, 170], styles))
    
    e.append(PageBreak())
    e.append(Paragraph("4. Kriteria Kelayakan dan Prosedur Promosi Jabatan", styles["h2"]))
    e.append(Paragraph("Promosi ke tingkat grading jabatan yang lebih tinggi mengharuskan bukti kesiapan kompetensi riil dan konsistensi rekam jejak. Persyaratan baku promosi:", styles["body"]))
    e.append(Paragraph("• <b>Masa Jabatan:</b> Menjalani masa kerja minimal 12 (dua belas) bulan pada grade posisi saat ini.", styles["bullet"]))
    e.append(Paragraph("• <b>Rekam Jejak Kinerja:</b> Meraih minimal 2 (dua) siklus evaluasi berturut-turut dengan predikat Rating 4 atau Rating 5.", styles["bullet"]))
    e.append(Paragraph("• <b>Dossier Promosi (Form PRM-301):</b> Pengajuan resmi wajib diajukan oleh Direktur Divisi melampirkan portofolio pencapaian bisnis dan rekomendasi People Partner.", styles["bullet"]))
    e.append(Paragraph("• <b>Penyesuaian Gaji Promosi:</b> Kenaikan gaji promosi minimal sebesar <b>10%</b> dari gaji pokok berjalan atau disesuaikan dengan nilai minimum rentang grade baru.", styles["body"]))
    
    e.append(Paragraph("5. Program Peningkatan Kinerja (Performance Improvement Plan - PIP)", styles["h2"]))
    e.append(Paragraph("Karyawan yang mendapatkan penilaian Rating 1 pada evaluasi akhir tahun atau Rating 2 selama dua kuartal berturut-turut wajib ditempatkan dalam Rencana Perbaikan Kinerja (PIP).", styles["body"]))
    
    pip_headers = ["Komponen PIP", "Ketentuan dan Tenggat Waktu", "Dokumen Terkait"]
    pip_rows = [
        ["Durasi Pelaksanaan PIP", "Tepat 60 (enam puluh) hari kalender terhitung sejak penandatanganan", "Formulir PIP-401"],
        ["Sesi Bimbingan (Coaching)", "Check-in mingguan (1-on-1) bersama Manajer langsung", "Log Aktivitas Mingguan"],
        ["Milestone Review 1", "Hari ke-30: Evaluasi formal pencapaian 50% target awal", "Laporan Evaluasi Paruh Waktu"],
        ["Milestone Review 2", "Hari ke-60: Evaluasi final penentuan kelulusan PIP", "Berita Acara Keputusan PIP"],
        ["Hasil PIP - Lulus", "Kinerja kembali ke standar; status karyawan normal", "Penutupan Kasus PIP"],
        ["Hasil PIP - Tidak Lulus", "Proses pemutusan hubungan kerja (PHK) sesuai ketentuan ketenagakerjaan", "Rekomendasi Pemutusan Hubungan Kerja"],
    ]
    e.append(style_table(pip_headers, pip_rows, [120, 240, 150], styles))
    e.append(Spacer(1, 8))
    e.append(Paragraph("Pihak yang terlibat dalam pemantauan PIP mencakup Karyawan yang bersangkutan, Atasan Langsung, dan People Business Partner (HRBP) sebagai mediator netral.", styles["body"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("PT Cymbal Indonesia adalah perusahaan fiktif. Dokumen ini adalah data demo untuk pengujian sistem Generative Search / RAG dan bukan nasihat hukum ketenagakerjaan.", styles["disclaimer"]))
    create_pdf(target, e)


def generate_id_doc_08(styles):
    target = ID_DOCS_DIR / "08_Kebijakan_Keamanan_Informasi_BYOD_dan_Privasi_Data.pdf"
    e = []
    e.append(Paragraph("PT CYMBAL INDONESIA · DIVISI TEKNOLOGI & KEAMANAN INFORMASI (INFOSEC)", styles["org_header"]))
    e.append(Paragraph("Kebijakan Keamanan Informasi, Perangkat Pribadi (BYOD), dan Privasi Data", styles["doc_title"]))
    e.append(Paragraph("Nomor: IT-SEC-012/2026 · Revisi 3 · Berlaku sejak 1 Januari 2026 · Pemilik: Chief Information Security Officer (CISO)", styles["meta_bar"]))
    
    e.append(Paragraph("1. Ruang Lingkup dan Kepatuhan Regulasi", styles["h2"]))
    e.append(Paragraph("Kebijakan ini mengikat seluruh karyawan, kontraktor, dan pihak ketiga yang mengakses sistem komputasi, jaringan data, dan informasi rahasia PT Cymbal Indonesia. Kebijakan ini dirancang mengacu pada standar <b>ISO/IEC 27001:2022</b> serta memenuhi ketentuan wajib <b>Undang-Undang No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)</b>.", styles["body"]))
    
    e.append(Paragraph("2. Kebijakan Penggunaan Perangkat Pribadi (Bring Your Own Device - BYOD)", styles["h2"]))
    e.append(Paragraph("Karyawan diperbolehkan menggunakan perangkat komputasi pribadi (laptop, smartphone, tablet) untuk mengakses email korporat dan platform kolaborasi Cymbal dengan syarat wajib:", styles["body"]))
    e.append(Paragraph("• <b>Registrasi MDM:</b> Perangkat wajib didaftarkan melalui Google Workspace Endpoint Management (MDM).", styles["bullet"]))
    e.append(Paragraph("• <b>Work Profile Sandboxing:</b> Data perusahaan harus berada di dalam profil kerja terenkripsi terpisah dari ruang penyimpanan pribadi.", styles["bullet"]))
    e.append(Paragraph("• <b>Enkripsi Drive Wajib:</b> Media penyimpanan laptop wajib dienkripsi penuh (BitLocker untuk Windows, FileVault untuk macOS, enkripsi hardware default untuk Android 11+ dan iOS 15+).", styles["bullet"]))
    e.append(Paragraph("• <b>Auto-Lock Layar:</b> Batas waktu layar terkunci otomatis (screen lock inactivity) maksimal <b>5 (lima) menit</b>.", styles["bullet"]))
    e.append(Paragraph("• <b>Larangan Perangkat Jailbreak/Rooted:</b> Perangkat yang dimodifikasi firmware-nya dilarang keras tersambung ke jaringan kerja.", styles["bullet"]))
    
    headers = ["Kategori Perangkat", "Sistem Operasi Minimum", "Status Enkripsi", "Aplikasi Wajib Terpasang"]
    rows = [
        ["Laptop Pribadi (macOS)", "macOS Ventura 13.0 atau terbaru", "FileVault 256-bit AES", "Google Endpoint Agent, CrowdStrike EDR"],
        ["Laptop Pribadi (Windows)", "Windows 11 Pro / Enterprise", "BitLocker Drive Encryption", "Google Endpoint Agent, CrowdStrike EDR"],
        ["Smartphone / Tablet (iOS)", "iOS 16.0 / iPadOS 16.0+", "Enkripsi Hardware Bawaan", "Google Device Policy, Work Profile"],
        ["Smartphone / Tablet (Android)", "Android 12.0 atau terbaru", "Full Disk Encryption Bawaan", "Android Enterprise Work Profile"],
    ]
    e.append(style_table(headers, rows, [130, 130, 110, 140], styles))
    e.append(Spacer(1, 8))
    
    e.append(PageBreak())
    e.append(Paragraph("3. Standar Autentikasi, Kata Sandi, dan Akses Zero-Trust VPN", styles["h2"]))
    e.append(Paragraph("Pengamanan kredensial akses korporat mengikuti ketentuan baku berikut:", styles["body"]))
    e.append(Paragraph("• <b>Kompleksitas Kata Sandi:</b> Panjang minimal <b>14 karakter</b>, memuat kombinasi huruf besar, huruf kecil, angka, dan simbol khusus.", styles["bullet"]))
    e.append(Paragraph("• <b>Masa Berlaku Sandi:</b> Wajib dirotasi setiap <b>90 hari kalender</b>. Sistem melarang penggunaan kembali 5 kata sandi terakhir.", styles["bullet"]))
    e.append(Paragraph("• <b>Multi-Factor Authentication (MFA):</b> Wajib mengaktifkan autentikasi 2 langkah berbasis FIDO2 Hardware Key (Titan/YubiKey) atau aplikasi Google Authenticator. Penggunaan SMS OTP dilarang untuk akses sistem kritikal.", styles["bullet"]))
    e.append(Paragraph("• <b>Akses Jaringan Cloud VPN:</b> Akses ke repositori source code, database staging/produksi, dan sistem SDM dari jaringan eksternal wajib melalui Cymbal Zero Trust Network Access (ZTNA) Cloud VPN. Penggunaan Wi-Fi publik tanpa VPN dilarang keras.", styles["bullet"]))
    
    e.append(Paragraph("4. Pelindungan Data Pribadi (UU PDP) dan Klasifikasi Informasi", styles["h2"]))
    e.append(Paragraph("Data diklasifikasikan ke dalam 4 kategori: Publik, Internal, Rahasia (Confidential), dan Sangat Rahasia (Strictly Confidential / PII). Data Pribadi sensitif karyawan atau pelanggan (NIK, rekam medis, nomor rekening, data biometrik) tidak boleh disimpan pada drive lokal tanpa izin tertulis Data Protection Officer (DPO). Karyawan dilarang memasukkan kode sumber atau dokumen rahasia ke platform Generative AI publik tanpa enkripsi enterprise.", styles["body"]))
    
    e.append(Paragraph("5. Prosedur Tanggap Darurat dan Pelaporan Insiden Keamanan (Form SEC-101)", styles["h2"]))
    e.append(Paragraph("Setiap kejadian kehilangan perangkat kerja, dugaan peretasan akun, atau tautan phishing yang terklik wajib dilaporkan segera:", styles["body"]))
    
    sec_headers = ["Tingkat Keparahan Insiden", "Contoh Kejadian", "Batas Waktu Pelaporan", "Eskalasi Penanganan"]
    sec_rows = [
        ["Level 1 - Kritis (P1)", "Data breach bocor ke publik, server terinfeksi ransomware", "Maksimal 1 Jam", "Tim CSIRT & CISO, Lapor Otoritas ≤ 72 jam"],
        ["Level 2 - Tinggi (P2)", "Laptop kantor hilang / dicuri, akses kredensial terkompromi", "Maksimal 2 Jam", "Remote Wipe profil kerja melalui MDM"],
        ["Level 3 - Sedang (P3)", "Menerima email phishing bertarget, virus terdeteksi EDR", "Maksimal 6 Jam", "Isolasi mesin endpoint oleh Tim Security Ops"],
        ["Pendaftaran Aset Baru", "Permohonan otorisasi perangkat BYOD baru", "H-3 sebelum pakai", "Pengisian Formulir Form SEC-101"],
    ]
    e.append(style_table(sec_headers, sec_rows, [110, 160, 110, 130], styles))
    e.append(Spacer(1, 8))
    e.append(Paragraph("Laporan insiden disampaikan melalui email darurat <b>security-ops@cymbal.co.id</b> atau hotline CSIRT <b>0811-SEC-CYM (0811-732-296)</b>.", styles["callout"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("PT Cymbal Indonesia adalah perusahaan fiktif. Dokumen ini adalah data demo untuk pengujian sistem Generative Search / RAG dan bukan nasihat hukum ketenagakerjaan.", styles["disclaimer"]))
    create_pdf(target, e)


def generate_id_doc_09(styles):
    target = ID_DOCS_DIR / "09_Program_Pengembangan_Karyawan_dan_Beasiswa.pdf"
    e = []
    e.append(Paragraph("PT CYMBAL INDONESIA · DIVISI TALENT & LEARNING DEVELOPMENT", styles["org_header"]))
    e.append(Paragraph("Program Pengembangan Kompetensi, Sertifikasi Profesional, dan Beasiswa S2", styles["doc_title"]))
    e.append(Paragraph("Nomor: LD-PGM-005/2026 · Revisi 2 · Berlaku sejak 1 Januari 2026 · Pemilik: Kepala Cymbal Academy & Talent Growth", styles["meta_bar"]))
    
    e.append(Paragraph("1. Filosofi Pembelajaran Berkelanjutan di Cymbal", styles["h2"]))
    e.append(Paragraph("PT Cymbal Indonesia percaya bahwa keunggulan organisasi berakar pada kapabilitas sumber daya manusianya. Perusahaan mengadopsi kerangka kerja pengembangan <b>70-20-10</b>: 70% pembelajaran melalui pengalaman kerja nyata dan rotasi proyek, 20% melalui pendampingan (mentoring & coaching), serta 10% melalui pendidikan dan sertifikasi formal terstruktur.", styles["body"]))
    
    e.append(Paragraph("2. Anggaran Pelatihan Individu Tahunan (Individual Learning Budget)", styles["h2"]))
    e.append(Paragraph("Setiap karyawan tetap (PKWTT) yang telah memiliki masa kerja minimal 6 bulan berhak atas alokasi anggaran pengembangan mandiri sebesar <b>Rp 15.000.000,- (lima belas juta rupiah)</b> per tahun kalender.", styles["body"]))
    e.append(Paragraph("Cakupan penggunaan anggaran individu mencakup:", styles["body"]))
    e.append(Paragraph("• Pembelian buku literatur bisnis, manajemen, dan rekayasa teknologi.", styles["bullet"]))
    e.append(Paragraph("• Langganan platform pembelajaran daring profesional (O'Reilly, Coursera, Pluralsight, Udemy).", styles["bullet"]))
    e.append(Paragraph("• Tiket keikutsertaan konferensi, seminar teknologi, dan lokakarya keahlian.", styles["bullet"]))
    e.append(Paragraph("• Biaya pendaftaran ujian sertifikasi keahlian teknis maupun manajerial.", styles["bullet"]))
    
    headers = ["Kategori Pengembangan", "Plafon Maksimal Tahunan", "Mekanisme Pembiayaan", "Syarat Kelayakan"]
    rows = [
        ["Anggaran Pelatihan Mandiri", "Rp 15.000.000,- / tahun", "Reimbursement Form LND-201", "Masa kerja ≥ 6 bulan"],
        ["Sertifikasi Strategis Divisi", "Didanai 100% Penuh (Di luar plafon)", "Direct Corporate Invoice", "Rekomendasi Vice President"],
        ["Ujian Sertifikasi Mandiri", "Sesuai sisa pagu anggaran individu", "Reimbursement dengan Sertifikat", "Nilai lulus minimum resmi"],
        ["Biaya Retake Ujian Gagal", "Maksimal 1 kali retake didanai", "Dipotong dari pagu tahunan", "Skor ujian pertama ≥ 80% passing"],
    ]
    e.append(style_table(headers, rows, [130, 130, 130, 120], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("3. Prosedur Penggantian Biaya Kursus dan Ujian (Form LND-201)", styles["h2"]))
    e.append(Paragraph("Klaim penggantian biaya diajukan melalui portal HRIS menggunakan <b>Formulir Klaim Sertifikasi & Pelatihan (Form LND-201)</b> paling lambat <b>30 (tiga puluh) hari kalender</b> setelah tanggal kelulusan ujian atau selesainya kegiatan. Pengajuan wajib melampirkan salinan sertifikat resmi kelulusan dan bukti pembayaran asli berstempel.", styles["body"]))
    
    e.append(PageBreak())
    e.append(Paragraph("4. Program Beasiswa Pascasarjana / S2 (Higher Degree Sponsorship)", styles["h2"]))
    e.append(Paragraph("Cymbal memberikan bantuan beasiswa pendidikan lanjutan jenjang Magister (S2) bagi talenta terbaik guna mencetak pemimpin masa depan korporat.", styles["body"]))
    
    s2_headers = ["Kriteria Seleksi Beasiswa", "Ketentuan Persyaratan Baku", "Keterangan Tambahan"]
    s2_rows = [
        ["Masa Kerja Minimum", "Minimal 2 (dua) tahun kerja berkelanjutan sebagai karyawan tetap", "Terhitung sejak pengangkatan PKWTT"],
        ["Rekam Jejak Kinerja", "Meraih minimal Rating 4 dalam 2 siklus evaluasi tahunan berturut-turut", "Dibuktikan riwayat HRIS"],
        ["Akreditasi Institusi", "Akreditasi A / Unggul (Nasional) atau Top 100 Dunia (QS World Ranking)", "Program studi relevan bisnis"],
        ["Porsi Pembiayaan", "Bantuan hingga 75% dari total biaya kuliah (Tuition Fee)", "Maksimal plafon Rp 150 jt"],
        ["Persetujuan Eksekutif", "Rekomendasi Direktur Divisi dan Persetujuan Komite Eksekutif HR", "Presentasi proposal studi"],
    ]
    e.append(style_table(s2_headers, s2_rows, [130, 220, 160], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("5. Masa Ikatan Dinas Beasiswa dan Penalti Pengunduran Diri", styles["h2"]))
    e.append(Paragraph("Penerima beasiswa S2 wajib menandatangani Perjanjian Ikatan Dinas sebelum memulai perkuliahan. Durasi ikatan dinas dihitung dengan rumus:", styles["body"]))
    e.append(Paragraph("<b>Masa Ikatan Dinas = 2n + 1 Tahun</b> (di mana <i>n</i> adalah masa studi resmi dalam hitungan tahun).", styles["callout"]))
    e.append(Paragraph("Sebagai contoh: Untuk program Magister dengan durasi 2 tahun (<i>n = 2</i>), masa ikatan dinas pasca-kelulusan adalah (2 × 2) + 1 = <b>5 (lima) tahun</b>.", styles["body"]))
    e.append(Paragraph("Konsekuensi Pengunduran Diri (Resignasi): Apabila karyawan mengundurkan diri sukarela sebelum masa ikatan dinas berakhir, karyawan wajib mengembalikan seluruh dana beasiswa yang telah dibayarkan secara prorata sisa masa dinas, ditambah denda penalti administratif sebesar <b>20%</b> dari total biaya yang diterima.", styles["body"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("PT Cymbal Indonesia adalah perusahaan fiktif. Dokumen ini adalah data demo untuk pengujian sistem Generative Search / RAG dan bukan nasihat hukum ketenagakerjaan.", styles["disclaimer"]))
    create_pdf(target, e)


def generate_id_doc_10(styles):
    target = ID_DOCS_DIR / "10_Prosedur_Terminasi_Resignasi_dan_Pesangon.pdf"
    e = []
    e.append(Paragraph("PT CYMBAL INDONESIA · DIVISI HUMAN CAPITAL & INDUSTRIAL RELATIONS", styles["org_header"]))
    e.append(Paragraph("Prosedur Terminasi, Resignasi Sukarela, dan Perhitungan Pesangon PP 35/2021", styles["doc_title"]))
    e.append(Paragraph("Nomor: HC-SOP-022/2026 · Revisi 4 · Berlaku sejak 1 Januari 2026 · Pemilik: Divisi Hubungan Industrial & Terminasi", styles["meta_bar"]))
    
    e.append(Paragraph("1. Ketentuan Pemberitahuan Pengunduran Diri (Notice Period)", styles["h2"]))
    e.append(Paragraph("Karyawan yang bermaksud mengakhiri hubungan kerja secara sukarela wajib menyampaikan surat pengunduran diri resmi tertulis melalui portal HRIS menggunakan <b>Formulir Pengunduran Diri (Form OFF-301)</b>:", styles["body"]))
    e.append(Paragraph("• <b>Staf & Individual Contributor (L1 s.d. L4):</b> Masa pemberitahuan tertulis (notice period) minimal <b>30 (tiga puluh) hari kalender</b> sebelum tanggal efektif berhenti bekerja.", styles["bullet"]))
    e.append(Paragraph("• <b>Level Manajer ke Atas (L5 s.d. L8):</b> Masa pemberitahuan minimal <b>60 (enam puluh) hari kalender</b> guna memastikan transisi manajerial dan alih pengetahuan proyek strategis.", styles["bullet"]))
    e.append(Paragraph("• <b>Penyelesaian Serah Terima (Handover):</b> Wajib menyelesaikan checklist serah terima tugas dan dokumen kerja yang diverifikasi oleh atasan langsung selambatnya H-3 hari kerja sebelum Hari Kerja Terakhir (Last Working Day).", styles["bullet"]))
    
    e.append(Paragraph("2. Prosedur Pengembalian Aset dan Inventaris Perusahaan", styles["h2"]))
    e.append(Paragraph("Pada hari kerja terakhir, karyawan wajib menyerahkan seluruh aset kepemilikan PT Cymbal Indonesia kepada bagian General Affairs dan IT Support:", styles["body"]))
    e.append(Paragraph("• Laptop dinas, charger, tas, serta monitor dan perlengkapan WFH tambahan.", styles["bullet"]))
    e.append(Paragraph("• Kartu tanda pengenal (ID Badge) gedung, kunci akses fisik, dan token perbankan perusahaan.", styles["bullet"]))
    e.append(Paragraph("• Kartu kredit korporat (Corporate Credit Card) beserta kuitansi pelunasan biaya operasional.", styles["bullet"]))
    e.append(Paragraph("• Seluruh dokumen arsip, softcopy rahasia perusahaan, dan data pelanggan.", styles["bullet"]))
    
    e.append(PageBreak())
    e.append(Paragraph("3. Matriks Perhitungan Kompensasi Pemutusan Hubungan Kerja (PP 35/2021)", styles["h2"]))
    e.append(Paragraph("Hak finansial karyawan akibat berakhirnya hubungan kerja diatur secara komprehensif mengacu pada ketentuan Peraturan Pemerintah No. 35 Tahun 2021. Komponen perhitungan mencakup Uang Pesangon (UP), Uang Penghargaan Masa Kerja (UPMK), dan Uang Penggantian Hak (UPH).", styles["body"]))
    
    pesangon_headers = ["Masa Kerja Karyawan", "Uang Pesangon (UP)", "Uang Penghargaan Masa Kerja (UPMK)", "Total Kompensasi Maksimal"]
    pesangon_rows = [
        ["Kurang dari 1 tahun", "1 bulan upah", "0 bulan upah", "1 bulan upah"],
        ["1 tahun s.d. < 2 tahun", "2 bulan upah", "0 bulan upah", "2 bulan upah"],
        ["2 tahun s.d. < 3 tahun", "3 bulan upah", "0 bulan upah", "3 bulan upah"],
        ["3 tahun s.d. < 4 tahun", "4 bulan upah", "2 bulan upah", "6 bulan upah"],
        ["4 tahun s.d. < 5 tahun", "5 bulan upah", "2 bulan upah", "7 bulan upah"],
        ["5 tahun s.d. < 6 tahun", "6 bulan upah", "2 bulan upah", "8 bulan upah"],
        ["6 tahun s.d. < 7 tahun", "7 bulan upah", "3 bulan upah", "10 bulan upah"],
        ["7 tahun s.d. < 8 tahun", "8 bulan upah", "3 bulan upah", "11 bulan upah"],
        ["8 tahun atau lebih", "9 bulan upah (Maksimal)", "Sesuai jenjang UPMK (hingga 10 bln)", "Maksimal 19 bulan upah"],
    ]
    e.append(style_table(pesangon_headers, pesangon_rows, [110, 110, 160, 130], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("4. Uang Penggantian Hak (UPH) dan Kompensasi Cuti Tahunan", styles["h2"]))
    e.append(Paragraph("Sesuai Pasal 40 ayat (4) PP 35/2021, karyawan berhak atas pencairan sisa cuti tahunan yang belum gugur dan belum diambil:", styles["body"]))
    e.append(Paragraph("<b>UPH Cuti = (Sisa Hari Cuti Tahunan / 21) × Gaji Pokok Bulanan</b>.", styles["callout"]))
    e.append(Paragraph("Uang Penggantian Hak dan gaji bulan berjalan dibayarkan secara utuh melalui transfer rekening bank penggajian pada jadwal siklus gajian terdekat.", styles["body"]))
    
    e.append(Paragraph("5. Dokumen Pasca-Terminasi dan Manfaat Jaminan Sosial", styles["h2"]))
    e.append(Paragraph("• <b>Surat Keterangan Pengalaman Kerja (Paklaring):</b> Diterbitkan oleh divisi Human Capital paling lambat <b>7 (tujuh) hari kerja</b> setelah tanggal pemutusan efektif.", styles["bullet"]))
    e.append(Paragraph("• <b>BPJS Ketenagakerjaan:</b> HC akan menonaktifkan kepesertaan dan menerbitkan formulir elektronik untuk pencairan saldo Jaminan Hari Tua (JHT) dan klaim manfaat Jaminan Kehilangan Pekerjaan (JKP).", styles["bullet"]))
    e.append(Paragraph("• <b>Exit Interview:</b> Wajib diselesaikan oleh karyawan sebelum pelepasan akses akun korporat.", styles["bullet"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("PT Cymbal Indonesia adalah perusahaan fiktif. Dokumen ini adalah data demo untuk pengujian sistem Generative Search / RAG dan bukan nasihat hukum ketenagakerjaan.", styles["disclaimer"]))
    create_pdf(target, e)


# ==============================================================================
# GLOBAL ENGLISH DOCUMENTS (05 to 10)
# ==============================================================================

def generate_en_doc_05(styles):
    target = EN_DOCS_DIR / "05_Global_Compensation_Overtime_and_Bonus_Plan.pdf"
    e = []
    e.append(Paragraph("CYMBAL CORP · GLOBAL TOTAL REWARDS & PEOPLE OPERATIONS", styles["org_header"]))
    e.append(Paragraph("Global Compensation, Overtime, and Incentive Bonus Plan", styles["doc_title"]))
    e.append(Paragraph("Policy No. HR-POL-105 · Version 3.1 · Effective January 1, 2026 · Owner: Global Total Rewards", styles["meta_bar"]))
    
    e.append(Paragraph("1. Purpose and Total Rewards Philosophy", styles["h2"]))
    e.append(Paragraph("Cymbal Corp is committed to maintaining a transparent, performance-driven compensation structure that attracts, motivates, and retains top global talent. Our compensation framework is benchmarked annually against Radford and Mercer tech sector surveys targeting the 75th percentile for total target compensation.", styles["body"]))
    
    e.append(Paragraph("2. Job Architecture & Salary Band Midpoints", styles["h2"]))
    e.append(Paragraph("All corporate roles are classified into standardized global job levels ranging from L3 to L8. Each level defines market-calibrated salary bands (Minimum, Midpoint, and Maximum):", styles["body"]))
    
    headers = ["Job Level", "Standard Role Title", "FLSA Exemption Status", "Target STI Bonus %", "RSU Equity Eligibility"]
    rows = [
        ["Level 3 (L3)", "Associate Specialist / Coordinator", "Non-Exempt (Overtime Eligible)", "5% Target STI", "Discretionary Spot Grant"],
        ["Level 4 (L4)", "Mid-Level Professional / Analyst", "Non-Exempt / Exempt by Role", "10% Target STI", "Standard Annual Grant"],
        ["Level 5 (L5)", "Senior Professional / Team Lead", "Exempt (Salaried Professional)", "15% Target STI", "Key Contributor Equity"],
        ["Level 6 (L6)", "Staff Specialist / Manager", "Exempt (Managerial / Tech Lead)", "25% Target STI", "Leadership Equity Plan"],
        ["Level 7 (L7)", "Principal / Senior Director", "Exempt (Senior Management)", "35% Target STI", "Executive Equity Tier"],
        ["Level 8 (L8)", "Vice President / Function Head", "Exempt (Executive Officer)", "50% Target STI", "Executive Long-Term Incentive"],
    ]
    e.append(style_table(headers, rows, [80, 150, 130, 80, 90], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("3. Overtime Policy for Non-Exempt Employees (FLSA)", styles["h2"]))
    e.append(Paragraph("Non-exempt employees working in excess of 40 active work hours in a defined 7-day payroll workweek are entitled to overtime pay calculated at <b>1.5× their regular hourly rate</b>. All overtime work must be pre-authorized by an immediate manager using <b>Form OT-101</b> in Workday. Mandatory meal breaks (minimum 30 minutes unpaid) must be logged for every shift extending beyond 5 consecutive hours.", styles["body"]))
    
    e.append(PageBreak())
    e.append(Paragraph("4. Short-Term Incentive (STI) Annual Performance Bonus", styles["h2"]))
    e.append(Paragraph("The Short-Term Incentive (STI) plan awards annual cash bonuses linked directly to corporate EBITDA targets and individual achievement ratings. The payout formula is defined as:", styles["body"]))
    e.append(Paragraph("<b>Annual Bonus Payout = Base Salary × Target STI % × Individual Rating Factor (0.0× – 1.5×) × Company Financial Multiplier (0.5× – 1.3×)</b>", styles["callout"]))
    
    bonus_headers = ["Individual Rating", "Performance Label", "Individual Multiplier", "Bonus Eligibility"]
    bonus_rows = [
        ["Rating 5", "Exceptional Impact", "1.30× to 1.50× Target", "Maximum Accelerated Pool"],
        ["Rating 4", "Exceeds Expectations", "1.10× to 1.25× Target", "Above Target Payout"],
        ["Rating 3", "Consistently Meets", "1.00× (100% Target)", "Target Payout Delivered"],
        ["Rating 2", "Developing / Inconsistent", "0.00× to 0.50× Target", "Discretionary Prorated Cap"],
        ["Rating 1", "Unsatisfactory Impact", "0.00× (No Payout)", "Ineligible for STI"],
    ]
    e.append(style_table(bonus_headers, bonus_rows, [90, 140, 130, 150], styles))
    e.append(Spacer(1, 8))
    e.append(Paragraph("Annual bonuses are disbursed in the first payroll cycle of March for employees actively employed prior to October 1 of the performance calendar year.", styles["body"]))
    
    e.append(Paragraph("5. Long-Term Incentive (LTI) & Restricted Stock Units (RSUs)", styles["h2"]))
    e.append(Paragraph("Equity awards are granted to eligible employees at Level 5 and above. RSUs follow a standard <b>4-year vesting schedule with a 1-year cliff</b>: 25% of granted shares vest on the 12-month anniversary of the grant date, and the remaining 75% vests in equal quarterly increments of <b>6.25%</b> over the subsequent 36 months.", styles["body"]))
    
    e.append(Paragraph("6. Payroll Administration and Form CMP-101", styles["h2"]))
    e.append(Paragraph("Salaries are paid on a bi-weekly cycle on alternating Fridays. Mandatory electronic direct deposit setup and tax withholding declarations must be completed through <b>Form CMP-101</b> in the employee self-service portal.", styles["body"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("Cymbal Corp is a fictional company. This document is for demonstration purposes in generative search and AI agent evaluation, not legal compensation advice.", styles["disclaimer"]))
    create_pdf(target, e)
    shutil.copy2(target, GLOBAL_DOCS_DIR / target.name)


def generate_en_doc_06(styles):
    target = EN_DOCS_DIR / "06_Global_Code_of_Conduct_Anti_Corruption_and_Whistleblowing.pdf"
    e = []
    e.append(Paragraph("CYMBAL CORP · GLOBAL COMPLIANCE, ETHICS & LEGAL AFFAIRS", styles["org_header"]))
    e.append(Paragraph("Global Code of Conduct, Anti-Corruption, and Whistleblower Protection", styles["doc_title"]))
    e.append(Paragraph("Policy No. COMP-POL-201 · Version 5.0 · Effective January 1, 2026 · Owner: Chief Compliance Officer", styles["meta_bar"]))
    
    e.append(Paragraph("1. Code of Conduct and Core Principles", styles["h2"]))
    e.append(Paragraph("Cymbal Corp conducts business under unwavering ethical standards. Every director, officer, and employee must observe strict compliance with applicable laws, including the <b>U.S. Foreign Corrupt Practices Act (FCPA)</b>, the <b>UK Bribery Act 2010</b>, and OECD anti-corruption conventions across all territories in which we operate.", styles["body"]))
    
    e.append(Paragraph("2. Anti-Bribery, Gifts, and Hospitality Thresholds", styles["h2"]))
    e.append(Paragraph("No employee or third-party agent acting on Cymbal's behalf may offer, solicit, or accept bribes, kickbacks, or inappropriate inducements. Modest business gifts and customary hospitality are permissible strictly within defined monetary thresholds:", styles["body"]))
    
    headers = ["Gift / Courtesy Category", "Permissible Value Limit", "Approval & Disclosure Rule", "Compliance Requirement"]
    rows = [
        ["Customary Promotional Items", "Under $100 per gift", "No prior approval required", "Branded pens, notepads, mugs"],
        ["Business Meals & Dining", "Up to $150 per person", "Substantiated in Concur expense", "Direct business purpose only"],
        ["Gifts Valued $100 to $250", "$100 to $250 aggregate", "Mandatory filing via Form ETH-101", "Written approval from VP"],
        ["Gifts Exceeding $250", "STRICTLY PROHIBITED", "Must be politely declined", "Surrender to charity raffle"],
        ["Gifts to Government Officials", "$0.00 (Zero Tolerance)", "Strict pre-clearance by Legal", "Immediate FCPA liability risk"],
    ]
    e.append(style_table(headers, rows, [130, 110, 140, 130], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("3. Annual Conflict of Interest Disclosure (Form COI-202)", styles["h2"]))
    e.append(Paragraph("All employees must avoid situations where personal interests conflict with Cymbal's business obligations. Every January, employees must complete the <b>Annual Conflict of Interest Disclosure (Form COI-202)</b> covering outside employment, advisory board seats, family ties to suppliers, and ownership stakes (>0.5%) in competing or partnering enterprises.", styles["body"]))
    
    e.append(PageBreak())
    e.append(Paragraph("4. Global Whistleblower Reporting Channels", styles["h2"]))
    e.append(Paragraph("Employees who witness or suspect fraud, accounting irregularities, harassment, bribery, or security violations are obligated to report them promptly through confidential channels managed by an independent third party (EthicsPoint):", styles["body"]))
    
    wbs_headers = ["Channel Type", "Contact Address / Number", "Availability & Security Features"]
    wbs_rows = [
        ["24/7 Ethics Hotline", "1-800-461-9330 (US) / +1-720-514-4400", "Toll-free, multilingual operators, 100% anonymous"],
        ["Secure Web Intake Portal", "https://ethics.cymbal.internal", "Encrypted intake, untracked IP logging"],
        ["Direct Compliance Email", "ethics-reporting@cymbal.com", "Routed exclusively to Chief Compliance Officer"],
        ["Audit Committee Mailbox", "audit-committee@cymbal.com", "Direct escalation for financial/executive misconduct"],
    ]
    e.append(style_table(wbs_headers, wbs_rows, [120, 180, 210], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("5. Absolute Non-Retaliation Guarantee", styles["h2"]))
    e.append(Paragraph("Cymbal strictly prohibits retaliation of any kind against an employee who reports a suspected violation in good faith or cooperates with an investigation. Any supervisor or colleague found engaging in retaliatory behavior (including termination, demotion, hostile behavior, or subtle performance downgrades) will face summary dismissal for cause and potential personal civil liability.", styles["body"]))
    
    e.append(Paragraph("6. Investigation Cadence and Governance", styles["h2"]))
    e.append(Paragraph("All reports receive preliminary triage within <b>48 hours</b>. Investigations are conducted under attorney-client privilege by Internal Audit and Legal, with formal resolution summaries submitted quarterly to the Audit Committee of the Board of Directors.", styles["body"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("Cymbal Corp is a fictional company. This document is for demonstration purposes in generative search and AI agent evaluation, not legal compliance advice.", styles["disclaimer"]))
    create_pdf(target, e)
    shutil.copy2(target, GLOBAL_DOCS_DIR / target.name)


def generate_en_doc_07(styles):
    target = EN_DOCS_DIR / "07_Performance_Calibration_Promotion_and_PIP_Guidelines.pdf"
    e = []
    e.append(Paragraph("CYMBAL CORP · GLOBAL TALENT & PEOPLE EXPERIENCE", styles["org_header"]))
    e.append(Paragraph("Performance Calibration, Merit Pay, Promotion Dossier, and PIP Framework", styles["doc_title"]))
    e.append(Paragraph("Policy No. TM-POL-305 · Version 4.0 · Effective January 1, 2026 · Owner: VP Global Talent Management", styles["meta_bar"]))
    
    e.append(Paragraph("1. Performance Management Philosophy", styles["h2"]))
    e.append(Paragraph("Cymbal Corp utilizes a continuous, transparent performance architecture centered on quarterly OKR alignment, semi-annual growth conversations, and an evidence-based annual talent calibration process. Our goal is to recognize outsized impact, reward merit objectively, and provide actionable development frameworks.", styles["body"]))
    
    e.append(Paragraph("2. 5-Tier Global Performance Rating Scale", styles["h2"]))
    headers = ["Rating Tier", "Performance Descriptor", "Contribution Definition", "Target Distribution"]
    rows = [
        ["Rating 5", "Exceptional Impact", "Transformational organizational impact, sets industry benchmarks (>125% OKRs)", "Target ~10%"],
        ["Rating 4", "Exceeds Expectations", "Consistently surpasses ambitious targets, models cultural leadership (110%-124%)", "Target ~25%"],
        ["Rating 3", "Consistently Meets", "Solid, dependable contributor achieving all core role deliverables (90%-109%)", "Target ~55%"],
        ["Rating 2", "Developing / Inconsistent", "Gaps identified in core deliverables or behavioral competencies (70%-89%)", "Target ~8%"],
        ["Rating 1", "Unsatisfactory Impact", "Substantial failure to meet baseline requirements (<70%), urgent intervention required", "Target ~2%"],
    ]
    e.append(style_table(headers, rows, [60, 130, 240, 80], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("3. Annual Merit Increase Matrix (Compa-Ratio Adjusted)", styles["h2"]))
    e.append(Paragraph("Merit salary adjustments are determined by cross-referencing an employee's performance rating with their compa-ratio (current base salary divided by band midpoint). Adjustments take effect annually on March 1.", styles["body"]))
    
    merit_headers = ["Performance Rating", "Compa < 85% (Below Mid)", "Compa 85% - 100% (Near Mid)", "Compa 100% - 115% (At/Above)", "Compa > 115% (High End)"]
    merit_rows = [
        ["Rating 5 (Exceptional)", "12.0% - 15.0%", "10.0% - 12.0%", "8.0% - 10.0%", "6.0% - 8.0%"],
        ["Rating 4 (Exceeds)", "8.0% - 10.0%", "6.5% - 8.0%", "5.0% - 6.5%", "3.5% - 5.0%"],
        ["Rating 3 (Meets)", "4.5% - 6.0%", "3.5% - 4.5%", "2.5% - 3.5%", "1.5% - 2.5%"],
        ["Rating 2 (Developing)", "0.0% - 1.5%", "0.0%", "0.0%", "0.0%"],
        ["Rating 1 (Unsatisfactory)", "0.0%", "0.0%", "0.0%", "0.0%"],
    ]
    e.append(style_table(merit_headers, merit_rows, [110, 100, 100, 100, 100], styles))
    
    e.append(PageBreak())
    e.append(Paragraph("4. Promotion Criteria and Dossier Submission (Form PRM-301)", styles["h2"]))
    e.append(Paragraph("Promotions represent an increase in scope, complexity, and business impact. Requirements for consideration:", styles["body"]))
    e.append(Paragraph("• <b>Time in Band:</b> Minimum of 12 months in current level prior to effective promotion date.", styles["bullet"]))
    e.append(Paragraph("• <b>Sustained High Performance:</b> At least two consecutive calibration cycles with Rating 4 or Rating 5.", styles["bullet"]))
    e.append(Paragraph("• <b>Promotion Dossier (Form PRM-301):</b> Nominating Director must submit an impact dossier including peer reviews, deliverable artifacts, and leadership readiness proof.", styles["bullet"]))
    e.append(Paragraph("• <b>Promotional Salary Adjustment:</b> Promotional increases average <b>8% to 15%</b> or adjust to the new band minimum, whichever is higher.", styles["body"]))
    
    e.append(Paragraph("5. Performance Improvement Plan (PIP) Protocol (Form PIP-401)", styles["h2"]))
    e.append(Paragraph("Employees receiving a Rating 1 rating or exhibiting sustained performance shortfalls are placed on a structured Performance Improvement Plan (PIP). Key milestones:", styles["body"]))
    
    pip_headers = ["PIP Phase", "Timeline & Frequency", "Action Items & Governance"]
    pip_rows = [
        ["Plan Initiation", "Day 1", "Signing of Form PIP-401 outlining SMART targets and coaching milestones"],
        ["Weekly Coaching", "Weeks 1 through 8", "Mandatory weekly 1-on-1 progress logging between Manager & Employee"],
        ["Formal Checkpoint 1", "Day 30 Milestone", "Interim evaluation; People Partner reviews progress evidence"],
        ["Final Evaluation", "Day 60 Milestone", "Formal determination: Successful Completion or Separation Initiation"],
        ["Outcome: Pass", "Day 60", "Employee restored to standard good standing"],
        ["Outcome: Fail", "Day 60+", "Separation initiated under Standard Severance Schedule guidelines"],
    ]
    e.append(style_table(pip_headers, pip_rows, [110, 120, 280], styles))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("Cymbal Corp is a fictional company. This document is for demonstration purposes in generative search and AI agent evaluation, not legal labor advice.", styles["disclaimer"]))
    create_pdf(target, e)
    shutil.copy2(target, GLOBAL_DOCS_DIR / target.name)


def generate_en_doc_08(styles):
    target = EN_DOCS_DIR / "08_Information_Security_BYOD_and_Acceptable_Use_Policy.pdf"
    e = []
    e.append(Paragraph("CYMBAL CORP · GLOBAL INFORMATION SECURITY (INFOSEC) & COMPLIANCE", styles["org_header"]))
    e.append(Paragraph("Enterprise Information Security, BYOD, Acceptable Use, and Data Privacy", styles["doc_title"]))
    e.append(Paragraph("Policy No. SEC-POL-401 · Version 5.2 · Effective January 1, 2026 · Owner: Chief Information Security Officer (CISO)", styles["meta_bar"]))
    
    e.append(Paragraph("1. Governance, Standards, and Regulatory Mandate", styles["h2"]))
    e.append(Paragraph("This policy establishes cybersecurity standards for all Cymbal Corp hardware, network infrastructure, data repositories, and digital communications. Cymbal maintains certified compliance with <b>SOC 2 Type II</b>, <b>ISO/IEC 27001:2022</b>, and adheres strictly to international data privacy statutes including the <b>EU General Data Protection Regulation (GDPR)</b> and <b>California Consumer Privacy Act (CCPA)</b>.", styles["body"]))
    
    e.append(Paragraph("2. Bring Your Own Device (BYOD) & Endpoint Controls", styles["h2"]))
    e.append(Paragraph("Employees authorized to access enterprise email, Slack, or documents via personal devices must strictly comply with mandatory endpoint hygiene rules:", styles["body"]))
    e.append(Paragraph("• <b>Google Workspace MDM Enrollment:</b> Personal mobile devices and laptops must be enrolled in Google Workspace Advanced Endpoint Management.", styles["bullet"]))
    e.append(Paragraph("• <b>Containerized Work Profiles:</b> Corporate data must reside inside an isolated Work Profile. Cymbal retains the right to execute a selective remote wipe of the corporate container without wiping personal photos or applications.", styles["bullet"]))
    e.append(Paragraph("• <b>Full Disk Encryption:</b> Hardware storage encryption must remain activated at all times (FileVault on macOS, BitLocker with TPM on Windows).", styles["bullet"]))
    e.append(Paragraph("• <b>Screen Inactivity Lock:</b> Automated screen lock required after a maximum of <b>5 minutes of inactivity</b>.", styles["bullet"]))
    e.append(Paragraph("• <b>No Rooted/Jailbroken Devices:</b> Any device with tampered kernel protections is immediately blocked by network access control.", styles["bullet"]))
    
    headers = ["Operating System", "Minimum Version", "Required Security Agent", "Encryption Standard"]
    rows = [
        ["Apple macOS", "macOS 13.0 (Ventura) or newer", "Google Endpoint Agent + CrowdStrike Falcon", "FileVault 2 XTS-AES-128"],
        ["Microsoft Windows", "Windows 11 Enterprise / Pro 22H2+", "Google Endpoint Agent + CrowdStrike Falcon", "BitLocker AES-256 with TPM 2.0"],
        ["Apple iOS / iPadOS", "iOS 16.0 or newer", "Google Device Policy Managed Profile", "Hardware AES-256 Crypto Engine"],
        ["Google Android", "Android 12.0 or newer", "Android Enterprise Work Container", "Hardware File-Based Encryption"],
    ]
    e.append(style_table(headers, rows, [120, 130, 140, 120], styles))
    e.append(Spacer(1, 8))
    
    e.append(PageBreak())
    e.append(Paragraph("3. Identity, Password Standards, and Multi-Factor Authentication", styles["h2"]))
    e.append(Paragraph("Credential security represents the first perimeter defense of corporate assets:", styles["body"]))
    e.append(Paragraph("• <b>Password Length & Entropy:</b> Minimum of <b>14 characters</b> containing at least one uppercase letter, one lowercase letter, one number, and one special symbol.", styles["bullet"]))
    e.append(Paragraph("• <b>Password Expiration:</b> Enforced rotation every <b>90 calendar days</b>. History buffer prevents reuse of the prior 10 passwords.", styles["bullet"]))
    e.append(Paragraph("• <b>Phishing-Resistant MFA:</b> Multi-Factor Authentication is mandatory across all accounts using FIDO2 hardware keys (Titan/YubiKey) or Google Authenticator. SMS and voice OTP are strictly prohibited.", styles["bullet"]))
    e.append(Paragraph("• <b>Zero-Trust Network Access (ZTNA) Cloud VPN:</b> Remote connections to production clusters, BigQuery data lakes, and internal developer tooling must tunnel through Cymbal ZTNA Cloud VPN. Connecting via public unencrypted Wi-Fi without active VPN is prohibited.", styles["bullet"]))
    
    e.append(Paragraph("4. Acceptable Use, PII Protection, and AI Tooling Guidelines", styles["h2"]))
    e.append(Paragraph("Personnel must safeguard customer Personally Identifiable Information (PII) and proprietary IP. Entering unredacted proprietary code, internal HR records, or confidential strategic plans into public commercial AI platforms is a direct violation of this policy. All automated pipelines must leverage dedicated enterprise GCP Vertex AI tenants.", styles["body"]))
    
    e.append(Paragraph("5. Security Incident Escalation Protocols (Form SEC-101)", styles["h2"]))
    e.append(Paragraph("Any suspected security incident (stolen device, unexpected login alert, clicked phishing payload) requires immediate escalation:", styles["body"]))
    
    sec_headers = ["Incident Classification", "Severity Scope", "Reporting SLA", "Response Actions"]
    sec_rows = [
        ["Severity 1 (Critical)", "Confirmed data breach, ransomware, infrastructure takeover", "Within 1 Hour", "CSIRT war-room, regulatory breach notice ≤ 72h"],
        ["Severity 2 (High)", "Lost/stolen laptop containing unencrypted data, admin compromise", "Within 2 Hours", "Immediate credential revocation, MDM device wipe"],
        ["Severity 3 (Medium)", "Suspicious phishing email, malware blocked by endpoint agent", "Within 8 Hours", "SOC containment and hash-block distribution"],
        ["Device Authorization", "Requesting new BYOD endpoint access approval", "3 Days Prior", "Filing of Endpoint Authorization Form SEC-101"],
    ]
    e.append(style_table(sec_headers, sec_rows, [110, 160, 90, 150], styles))
    e.append(Spacer(1, 8))
    e.append(Paragraph("Emergency incident notifications must be transmitted immediately to <b>infosec-incident@cymbal.com</b> or the 24/7 Security Hotline at <b>+1-888-555-CYM-SEC</b>.", styles["callout"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("Cymbal Corp is a fictional company. This document is for demonstration purposes in generative search and AI agent evaluation, not legal cybersecurity advice.", styles["disclaimer"]))
    create_pdf(target, e)
    shutil.copy2(target, GLOBAL_DOCS_DIR / target.name)


def generate_en_doc_09(styles):
    target = EN_DOCS_DIR / "09_Learning_Development_and_Tuition_Assistance_Program.pdf"
    e = []
    e.append(Paragraph("CYMBAL CORP · GLOBAL TALENT DEVELOPMENT & CYMBAL ACADEMY", styles["org_header"]))
    e.append(Paragraph("Learning & Development, Professional Certification, and Tuition Assistance", styles["doc_title"]))
    e.append(Paragraph("Policy No. LND-POL-501 · Version 3.0 · Effective January 1, 2026 · Owner: Chief Learning Officer", styles["meta_bar"]))
    
    e.append(Paragraph("1. Growth Philosophy and Career Framework", styles["h2"]))
    e.append(Paragraph("Cymbal Corp fosters a culture of relentless learning and technical excellence. Rooted in the <b>70-20-10 learning model</b>, we empower employees to expand their professional mastery through real-world stretch assignments (70%), mentorship and cross-functional guilds (20%), and sponsored continuing education and formal certifications (10%).", styles["body"]))
    
    e.append(Paragraph("2. Annual Individual Professional Development Stipend", styles["h2"]))
    e.append(Paragraph("Every regular full-time employee with at least 90 days of continuous service is allotted an annual individual development stipend of <b>$2,500 USD per calendar year</b>.", styles["body"]))
    e.append(Paragraph("Eligible expenses reimbursable under this stipend include:", styles["body"]))
    e.append(Paragraph("• Registration fees for approved technical, leadership, and industry conferences.", styles["bullet"]))
    e.append(Paragraph("• Professional association memberships (ACM, IEEE, SHRM, AICPA, etc.).", styles["bullet"]))
    e.append(Paragraph("• Technical reference books, technical journals, and specialized self-paced online curricula.", styles["bullet"]))
    e.append(Paragraph("• Examination fees for recognized professional credentials (GCP, AWS, CISSP, PMP, CFA, etc.).", styles["bullet"]))
    
    headers = ["Program Element", "Annual Benefit Ceiling", "Payment Mechanism", "Prerequisite Criteria"]
    rows = [
        ["Annual Individual Stipend", "$2,500 USD per calendar year", "Expense reimbursement via Concur", "Full-time status, ≥ 90 days tenure"],
        ["Enterprise Sponsored Certs", "100% Fully Covered (Outside stipend)", "Corporate voucher direct bill", "VP / Functional Head recommendation"],
        ["Higher Ed Tuition (Sec 127)", "Up to $5,250 USD annually tax-free", "Direct bursar / post-term payout", "≥ 12 months tenure, Grade B or higher"],
        ["Exam Retake Coverage", "One retake covered if score ≥ 80%", "Deducted from individual stipend", "Passing credential on second attempt"],
    ]
    e.append(style_table(headers, rows, [130, 130, 130, 120], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("3. Reimbursement Procedure and Form LND-201", styles["h2"]))
    e.append(Paragraph("Reimbursement claims must be submitted within <b>45 calendar days</b> of course or credential completion via Concur using <b>Form LND-201 (Certification & Training Reimbursement)</b>. Claims must include itemized paid receipts and official certificates of completion or credential score reports.", styles["body"]))
    
    e.append(PageBreak())
    e.append(Paragraph("4. Higher Education Tuition Assistance Program (IRS Section 127)", styles["h2"]))
    e.append(Paragraph("Under IRC Section 127, Cymbal provides up to <b>$5,250 per calendar year</b> in tax-free tuition reimbursement for accredited undergraduate and graduate coursework aligned with the employee's career progression at Cymbal.", styles["body"]))
    
    s2_headers = ["Program Requirement", "Standard Threshold", "Operational Detail"]
    s2_rows = [
        ["Tenure Eligibility", "12 months continuous full-time service", "Measured prior to academic term start date"],
        ["Performance Requirement", "Rating 3 (Consistently Meets) or above", "Most recent annual calibration cycle"],
        ["Institution Standard", "Regionally accredited college or university", "Non-accredited institutions ineligible"],
        ["Academic Standard", "Minimum grade of 'B' (3.0 GPA) or 'Pass'", "Grades below 'B' ineligible for reimbursement"],
        ["Pre-Enrollment Approval", "Mandatory filing via Form LND-302", "Must be submitted 30 days prior to term start"],
    ]
    e.append(style_table(s2_headers, s2_rows, [130, 180, 200], styles))
    e.append(Spacer(1, 8))
    
    e.append(Paragraph("5. Post-Completion Retention Agreement and Repayment Covenant", styles["h2"]))
    e.append(Paragraph("To protect organizational investments in advanced degrees, employees receiving Tuition Assistance agree to a <b>12-month service retention covenant</b> beginning on the official completion date of the subsidized academic course:", styles["body"]))
    e.append(Paragraph("• <b>Departure within 0 to 6 months:</b> Employee must repay <b>100%</b> of tuition assistance disbursed for that course.", styles["bullet"]))
    e.append(Paragraph("• <b>Departure within 7 to 12 months:</b> Employee must repay <b>50%</b> of tuition assistance disbursed for that course.", styles["bullet"]))
    e.append(Paragraph("• <b>Departure after 12 months:</b> No repayment obligation is incurred.", styles["bullet"]))
    e.append(Paragraph("Repayment obligations are waived exclusively in instances of company-initiated separation due to organizational restructuring or reduction-in-force (RIF).", styles["body"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("Cymbal Corp is a fictional company. This document is for demonstration purposes in generative search and AI agent evaluation, not legal labor advice.", styles["disclaimer"]))
    create_pdf(target, e)
    shutil.copy2(target, GLOBAL_DOCS_DIR / target.name)


def generate_en_doc_10(styles):
    target = EN_DOCS_DIR / "10_Offboarding_Severance_and_Separation_Policy.pdf"
    e = []
    e.append(Paragraph("CYMBAL CORP · GLOBAL EMPLOYEE RELATIONS & LEGAL OPERATIONS", styles["org_header"]))
    e.append(Paragraph("Offboarding, Voluntary Resignation, Severance Schedule, and Separation", styles["doc_title"]))
    e.append(Paragraph("Policy No. ER-POL-602 · Version 4.1 · Effective January 1, 2026 · Owner: Head of Global Employee Relations", styles["meta_bar"]))
    
    e.append(Paragraph("1. Voluntary Resignation Protocol & Required Notice Periods", styles["h2"]))
    e.append(Paragraph("Employees resigning voluntarily must submit formal written notice through the HR Service Center utilizing <b>Separation Notice Form OFF-301</b>:", styles["body"]))
    e.append(Paragraph("• <b>Individual Contributors & Specialists (L3 through L5):</b> Minimum <b>2 weeks (14 calendar days)</b> advance written notice.", styles["bullet"]))
    e.append(Paragraph("• <b>People Managers & Senior Leaders (L6 and above):</b> Minimum <b>4 weeks (30 calendar days)</b> advance written notice to support executive succession.", styles["bullet"]))
    e.append(Paragraph("• <b>Garden Leave Provision:</b> Cymbal reserves the right to place departing employees on paid garden leave or accelerate the effective last working day with full pay in lieu of notice.", styles["bullet"]))
    
    e.append(Paragraph("2. Asset Recovery and Digital Access Deprovisioning", styles["h2"]))
    e.append(Paragraph("On or before the employee's Last Day of Work (LDW), all corporate physical assets and intellectual property must be surrendered:", styles["body"]))
    e.append(Paragraph("• Corporate MacBook/laptop, chargers, external displays, and hardware authentication tokens.", styles["bullet"]))
    e.append(Paragraph("• Corporate building access badges and parking passes.", styles["bullet"]))
    e.append(Paragraph("• Corporate procurement credit cards with final expense reconciliations attached.", styles["bullet"]))
    e.append(Paragraph("Digital access to corporate systems (Google Workspace, Slack, VPN, GitHub) is systematically revoked at <b>17:00 local time</b> on the employee's last day of work.", styles["body"]))
    
    e.append(PageBreak())
    e.append(Paragraph("3. Involuntary Separation and Standard Severance Schedule", styles["h2"]))
    e.append(Paragraph("In cases of involuntary termination due to organizational restructuring, position elimination, or mutual separation agreements (excluding termination for gross misconduct or cause), eligible employees receive severance benefits:", styles["body"]))
    
    headers = ["Completed Years of Service", "Base Severance Entitlement", "COBRA Healthcare Subsidy", "Outplacement Coaching"]
    rows = [
        ["Less than 1 Year", "4 Weeks Base Pay (Minimum Floor)", "1 Month Fully Subsidized", "1 Month Career Transition"],
        ["1 to 2 Years", "4 Weeks Base Pay", "2 Months Fully Subsidized", "2 Months Career Transition"],
        ["3 to 4 Years", "6 to 8 Weeks Base Pay (2 wks/yr)", "2 Months Fully Subsidized", "3 Months Career Transition"],
        ["5 to 7 Years", "10 to 14 Weeks Base Pay (2 wks/yr)", "3 Months Fully Subsidized", "3 Months Career Transition"],
        ["8 to 10 Years", "16 to 20 Weeks Base Pay (2 wks/yr)", "3 Months Fully Subsidized", "6 Months Executive Coaching"],
        ["11+ Years of Service", "2 Weeks per Year (Max 26 Weeks)", "3 Months Fully Subsidized", "6 Months Executive Coaching"],
    ]
    e.append(style_table(headers, rows, [120, 150, 120, 120], styles))
    e.append(Spacer(1, 8))
    e.append(Paragraph("Severance disbursements require execution of a standard Separation Agreement and General Release of Claims within statutory consideration windows (21 or 45 days under ADEA / OWBPA).", styles["callout"]))
    
    e.append(Paragraph("4. Accrued Unused PTO Payout", styles["h2"]))
    e.append(Paragraph("Accrued, unused Paid Time Off (PTO) is paid out in full on the final paycheck in accordance with state and regional wage laws. The payout is calculated using the employee's final effective regular hourly rate:", styles["body"]))
    e.append(Paragraph("<b>PTO Payout Amount = Unused PTO Hours × (Annual Base Salary / 2,080)</b>", styles["callout"]))
    
    e.append(Paragraph("5. Benefits Continuation, 401(k) Rollover, and Employment Verification", styles["h2"]))
    e.append(Paragraph("• <b>COBRA Healthcare Election:</b> COBRA enrollment packets are mailed by our third-party administrator within 14 calendar days post-termination.", styles["bullet"]))
    e.append(Paragraph("• <b>401(k) Retirement Account:</b> Vested 401(k) balances remain with Fidelity; departing employees may maintain their balance or initiate a direct rollover.", styles["bullet"]))
    e.append(Paragraph("• <b>Equity Option Exercise Window:</b> Standard post-termination option exercise window is <b>90 days</b> from separation date.", styles["bullet"]))
    e.append(Paragraph("• <b>Reference & Verification:</b> Standard verification verifies only job titles and dates of employment via The Work Number (Code: CYM-1092).", styles["bullet"]))
    
    e.append(Spacer(1, 14))
    e.append(Paragraph("Cymbal Corp is a fictional company. This document is for demonstration purposes in generative search and AI agent evaluation, not legal employment advice.", styles["disclaimer"]))
    create_pdf(target, e)
    shutil.copy2(target, GLOBAL_DOCS_DIR / target.name)


def main():
    print("Starting generation of expanded 10 enterprise HR policy documents...")
    styles = build_styles()
    
    print("\n--- Generating Indonesian Corpus (05 - 10) ---")
    generate_id_doc_05(styles)
    generate_id_doc_06(styles)
    generate_id_doc_07(styles)
    generate_id_doc_08(styles)
    generate_id_doc_09(styles)
    generate_id_doc_10(styles)
    
    print("\n--- Generating Global English Corpus (05 - 10) ---")
    generate_en_doc_05(styles)
    generate_en_doc_06(styles)
    generate_en_doc_07(styles)
    generate_en_doc_08(styles)
    generate_en_doc_09(styles)
    generate_en_doc_10(styles)
    
    print("\n✓ Successfully created all 12 expanded documents across ID and EN corpora!")


if __name__ == "__main__":
    main()
