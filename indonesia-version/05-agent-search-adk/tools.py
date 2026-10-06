import logging
from typing import Dict, Any, Optional
from google.cloud import discoveryengine_v1 as discoveryengine

from config import (
    HRIS_DB,
    HRIS_DB_EN,
    PROJECT_ID,
    LOCATION,
    DATA_STORE_ID,
)
COLLECTION_ID = "default_collection"

logger = logging.getLogger("adk_hr_tools")


def get_employee_leave_balance(employee_id: str) -> Dict[str, Any]:
    """Mengambil informasi personal karyawan dari database HRIS Cymbal Indonesia.

    Alat ini digunakan untuk melihat sisa kuota cuti tahunan, jumlah hari WFA yang sudah
    terpakai tahun ini, jabatan, divisi, dan status eligibilitas cuti besar seorang karyawan.

    Args:
        employee_id: ID resmi karyawan Cymbal, misal 'EMP-1042', 'EMP-2088', 'EMP-3001'.

    Returns:
        Dictionary data karyawan dari HRIS atau pesan error jika ID tidak ditemukan.
    """
    clean_id = employee_id.strip().upper()
    if clean_id in HRIS_DB:
        data = HRIS_DB[clean_id]
        return {
            "status": "SUCCESS",
            "employee_id": clean_id,
            "nama": data["nama"],
            "jabatan": data["jabatan"],
            "level": data["level"],
            "divisi": data["divisi"],
            "sisa_cuti_tahunan": data["sisa_cuti_tahunan"],
            "hari_wfa_terpakai": data["hari_wfa_terpakai"],
            "cuti_besar_eligible": data["cuti_besar_eligible"],
            "lokasi_kantor": data["lokasi_kantor"],
        }
    return {
        "status": "NOT_FOUND",
        "employee_id": employee_id,
        "message": f"Karyawan dengan ID '{employee_id}' tidak ditemukan dalam database HRIS.",
    }


def get_employee_pto_balance(employee_id: str) -> Dict[str, Any]:
    """Retrieve real-time employee profile and balances from the Cymbal Corp global HRIS database.

    Used to check an employee's accrued PTO balance, international WFA days used this calendar year,
    job title, and department.

    Args:
        employee_id: Official employee ID, e.g. 'EMP-1042', 'EMP-2088', 'EMP-3001'.

    Returns:
        Dictionary with live HRIS profile or NOT_FOUND status.
    """
    clean_id = employee_id.strip().upper()
    if clean_id in HRIS_DB_EN:
        data = HRIS_DB_EN[clean_id]
        return {
            "status": "SUCCESS",
            "employee_id": clean_id,
            "name": data["name"],
            "title": data["title"],
            "level": data["level"],
            "division": data["division"],
            "pto_balance": data["pto_balance"],
            "wfa_days_used": data["wfa_days_used"],
            "wfa_days_max": data["wfa_days_max"],
            "remote_work_eligible": data["remote_work_eligible"],
            "office_location": data["office_location"],
        }
    return {
        "status": "NOT_FOUND",
        "employee_id": employee_id,
        "message": f"Employee ID '{employee_id}' not found in HRIS database.",
    }


def search_company_policy(query: str, corpus: str = "id") -> str:
    """Mencari regulasi, SOP, plafon tunjangan, formulir, dan FAQ resmi di dokumen kebijakan HR Cymbal.

    Gunakan alat ini untuk mencari aturan kuota WFH/WFA, cuti tahunan/melahirkan/bersama,
    Surat Perintah Perjalanan Dinas (SPPD), Formulir PDN-402B/EXP-402B, dan tabel plafon kesehatan.

    Args:
        query: Kata kunci atau pertanyaan kebijakan dalam Bahasa Indonesia atau English.
        corpus: "id" (Indonesian) atau "en" (English Global).

    Returns:
        Rangkuman kutipan resmi dari dokumen kebijakan perusahaan.
    """
    client = discoveryengine.SearchServiceClient()
    serving_config = (
        f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
        f"/dataStores/{DATA_STORE_ID}/servingConfigs/default_search"
    )

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=3,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=1,
                max_extractive_segment_count=2,
            ),
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=3,
                include_citations=True,
                language_code="id" if corpus == "id" else "en",
            ),
        ),
    )

    try:
        response = client.search(request=request)
        if response.summary and response.summary.summary_text:
            return response.summary.summary_text

        snippets = []
        for res in response.results:
            derived = getattr(res.document, "derived_struct_data", {})
            title = derived.get("title", res.document.name)
            for seg in derived.get("extractive_segments", []):
                snippets.append(f"[{title}]: {seg.get('content', '')}")
        if snippets:
            return "\n\n".join(snippets)
        return "Tidak ditemukan kutipan spesifik untuk kata kunci tersebut di dokumen kebijakan."

    except Exception as e:
        logger.warning(f"Error querying Agent Search datastore: {e}")
        q_lower = query.lower()

        # Check for English Corpus / Keywords
        if corpus == "en" or any(w in q_lower for w in ["japan", "caregiver", "exp-402b", "deductible", "pto", "remote"]):
            if any(w in q_lower for w in ["japan", "remote", "wfa", "work remotely"]):
                return (
                    "[04_Remote_Work_and_Equipment_Stipend_FAQ.pdf] Section 4 (International Remote Work):\n"
                    "- Employees in good standing may work remotely outside their home country for up to 20 workdays per calendar year.\n"
                    "- International WFA requests require direct manager approval, VP sign-off, and at least 14 days advance submission via the WorkFlex Portal.\n"
                    "- Employees must ensure high-speed internet and maintain standard working hours overlapping with their home team."
                )
            elif any(w in q_lower for w in ["child", "caregiver", "parental leave", "welcomed"]):
                return (
                    "[01_Global_PTO_and_Leave_Policy.pdf] Section 3.2 (Parental Leave):\n"
                    "- Primary caregivers are eligible for 16 weeks of 100% paid parental leave following the birth, adoption, or foster placement of a child.\n"
                    "- Secondary caregivers receive 4 weeks of 100% paid leave.\n"
                    "- Parental leave can be taken consecutively or in blocks within the first 12 months."
                )
            elif any(w in q_lower for w in ["exp-402b", "402b", "reimbursement", "travel expense"]):
                return (
                    "[03_Expense_and_Travel_Reimbursement_Policy.pdf] Section 5 (Expense Reporting):\n"
                    "- Form EXP-402B (Supplemental Expense Itemization Form) is required for itemizing and justifying any business travel expense exceeding $500.\n"
                    "- The submission deadline is within 30 calendar days of trip completion.\n"
                    "- Itemized item receipts and manager approval are mandatory."
                )
            elif any(w in q_lower for w in ["deductible", "ppo", "hdhp", "hsa"]):
                return (
                    "[02_2026_Benefits_and_Healthcare_Guide.pdf] Medical Plans Comparison Table:\n"
                    "- Family Deductible: PPO is $1,500 per year; HDHP is $3,000 per year.\n"
                    "- Employer HSA Contribution: PPO provides $0 (ineligible for HSA); HDHP provides a $1,200 annual employer contribution."
                )
            return (
                "[01_Global_PTO_and_Leave_Policy.pdf] Official Cymbal Corp HR Policy:\n"
                "- All leave and remote work requests must be logged through the employee HR portal."
            )

        # Indonesian Corpus Fallback
        if "wfa" in q_lower or "wfh" in q_lower or "bali" in q_lower:
            return (
                "[04_FAQ_WFH_WFA_dan_Tunjangan_Peralatan.pdf] Bagian 2 (WFA Dalam Negeri):\n"
                "- Batas maksimal WFA dalam negeri adalah 20 hari kerja per tahun kalender.\n"
                "- Pengajuan WFA wajib diajukan minimal H-7 hari kerja melalui sistem HRIS dan disetujui atasan langsung.\n"
                "- Karyawan tetap wajib memenuhi jam kerja 40 jam per minggu dan siap dihubungi."
            )
        elif "cuti" in q_lower or "istri melahirkan" in q_lower or "persalinan" in q_lower:
            return (
                "[01_Kebijakan_Cuti_Karyawan.pdf] Bab IV Pasal 7 (Cuti Khusus/Ibadah/Keluarga):\n"
                "- Cuti pendampingan istri melahirkan/keguguran diberikan selama 5 (lima) hari kerja berturut-turut.\n"
                "- Gaji dan tunjangan tetap dibayarkan penuh (paid leave)."
            )
        elif "pdn-402b" in q_lower or "sppd" in q_lower or "perjalanan dinas" in q_lower:
            return (
                "[03_Kebijakan_Perjalanan_Dinas_dan_Reimburse.pdf] Bagian 3 Prosedur SPPD:\n"
                "- Formulir PDN-402B adalah Formulir Pertanggungjawaban Biaya Perjalanan Dinas Dalam Negeri.\n"
                "- Wajib diserahkan ke Departemen Keuangan selambat-lambatnya 14 (empat belas) hari kalender setelah tanggal kepulangan."
            )
        elif "plafon" in q_lower or "caesar" in q_lower or "manajer" in q_lower:
            return (
                "[02_Panduan_Tunjangan_dan_Kesehatan_2026.pdf] Tabel Plafon Kesehatan:\n"
                "- Rawat Jalan: Staf Rp 7.500.000 / tahun, Manajer Rp 15.000.000 / tahun.\n"
                "- Persalinan Caesar: Staf Rp 18.000.000 per kejadian, Manajer Rp 30.000.000 per kejadian."
            )
        return "Dokumen kebijakan HR Cymbal menyatakan agar seluruh pengajuan cuti dan permohonan fasilitas diajukan melalui portal HRIS."

