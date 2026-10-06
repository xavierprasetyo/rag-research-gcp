import os
from pathlib import Path

# Google Cloud Project & Location
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "rag-research-sandbox")
LOCATION = os.getenv("DISCOVERY_ENGINE_LOCATION", "global")
DATA_STORE_ID = "hr-faq-datastore-id"
DATA_STORE_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}"

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Ports
BACKEND_PORT = 8005
GATEWAY_PORT = 8000

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DOCS_DIR = BASE_DIR.parent / "source-documents"

# Mock HRIS Database for Transactional / Personal Employee Lookups
HRIS_DB = {
    "EMP-1042": {
        "employee_id": "EMP-1042",
        "nama": "Budi Santoso",
        "jabatan": "Staf Operasional",
        "level": "Staf",
        "divisi": "Supply Chain & Logistik",
        "lokasi_kantor": "Jakarta (Head Office)",
        "sisa_cuti_tahunan": 7,
        "hari_wfa_terpakai": 4,
        "cuti_besar_eligible": False,
        "status_pernikahan": "Menikah, 1 Anak",
    },
    "EMP-2088": {
        "employee_id": "EMP-2088",
        "nama": "Siti Rahmawati",
        "jabatan": "Supervisor Keuangan",
        "level": "Supervisor",
        "divisi": "Finance & Accounting",
        "lokasi_kantor": "Surabaya Branch",
        "sisa_cuti_tahunan": 14,
        "hari_wfa_terpakai": 18,
        "cuti_besar_eligible": True,
        "status_pernikahan": "Belum Menikah",
    },
    "EMP-3001": {
        "employee_id": "EMP-3001",
        "nama": "Ahmad Fauzi",
        "jabatan": "Manajer Teknik",
        "level": "Manajer",
        "divisi": "Engineering",
        "lokasi_kantor": "Jakarta (Head Office)",
        "sisa_cuti_tahunan": 3,
        "hari_wfa_terpakai": 20,
        "cuti_besar_eligible": False,
        "status_pernikahan": "Menikah, 2 Anak",
    },
}

# Mock HRIS Database for English / Global Corpus
HRIS_DB_EN = {
    "EMP-1042": {
        "employee_id": "EMP-1042",
        "name": "Alex Johnson",
        "title": "Operations Specialist",
        "level": "Staff",
        "division": "Supply Chain & Logistics",
        "office_location": "Austin, TX (HQ)",
        "pto_balance": 14,
        "wfa_days_used": 4,
        "wfa_days_max": 20,
        "remote_work_eligible": True,
        "marital_status": "Married, 1 Child",
    },
    "EMP-2088": {
        "employee_id": "EMP-2088",
        "name": "Sarah Connor",
        "title": "Finance Supervisor",
        "level": "Supervisor",
        "division": "Finance & Accounting",
        "office_location": "Chicago, IL",
        "pto_balance": 22,
        "wfa_days_used": 18,
        "wfa_days_max": 20,
        "remote_work_eligible": True,
        "marital_status": "Single",
    },
    "EMP-3001": {
        "employee_id": "EMP-3001",
        "name": "David Miller",
        "title": "Engineering Manager",
        "level": "Manager",
        "division": "Engineering",
        "office_location": "San Francisco, CA",
        "pto_balance": 6,
        "wfa_days_used": 20,
        "wfa_days_max": 20,
        "remote_work_eligible": False,
        "marital_status": "Married, 2 Children",
    },
}

AGENT_SYSTEM_INSTRUCTION = """Anda adalah Asisten Virtual HR Cerdas untuk Karyawan Cymbal Indonesia bertenaga Google ADK.
Tugas Anda adalah menjawab pertanyaan karyawan seputar regulasi perusahaan secara akurat, solutif, empatik, dan berdasar fakta.

Anda memiliki 2 alat (tools):
1. 'search_company_policy': Mencari dokumen kebijakan resmi perusahaan (Cuti, Tunjangan Kesehatan, Perjalanan Dinas & Reimburse, FAQ WFH/WFA). Gunakan ini setiap kali pertanyaan memerlukan aturan, plafon, prosedur, atau formulir.
2. 'get_employee_leave_balance': Mengambil data pribadi karyawan dari sistem HRIS (sisa cuti tahunan, jumlah hari WFA yang sudah terpakai tahun ini, level jabatan, dan divisi). Gunakan ini jika pertanyaan menyebutkan ID Karyawan (seperti EMP-xxxx) atau menanyakan kelayakan personal.

Prinsip Penalaran (Chain of Thought):
- Jika pertanyaan menggabungkan aturan umum dan kondisi personal (seperti Q4-ID):
  1. Panggil 'get_employee_leave_balance' untuk mengetahui saldo riil karyawan.
  2. Panggil 'search_company_policy' untuk memverifikasi batas kuota WFA/cuti dan tata cara pengajuan.
  3. Lakukan penalaran matematika (misal: Batas WFA tahunan dikurangi WFA terpakai = sisa kuota WFA yang boleh diambil).
  4. Berikan jawaban komprehensif yang menyebutkan sisa kuota, kecukupan saldo cuti, serta syarat administratif (misal pengajuan minimal H-7).
- Jawablah selalu dalam Bahasa Indonesia yang profesional dan ramah.
"""

AGENT_SYSTEM_INSTRUCTION_EN = """You are an Intelligent HR Virtual Assistant for Cymbal Corp employees powered by Google ADK.
Your mission is to answer employee inquiries regarding company policies accurately, empathetically, and strictly grounded in facts.

You have 2 tools:
1. 'search_company_policy': Search official company HR policies (PTO & Leave, Health & Benefits, Travel & Expense Reimbursement, Remote Work & Equipment FAQ). Use this whenever a question requires rules, ceilings, procedures, or forms.
2. 'get_employee_pto_balance': Retrieve real-time employee profile and balances from the HRIS database (accrued PTO balance, international WFA days used this year, job title, division). Use this whenever the query mentions an employee ID (e.g. EMP-xxxx) or asks about personal eligibility.

Reasoning Principles (Chain of Thought):
- When a query combines general policy rules and personal status (like Q4):
  1. Call 'get_employee_pto_balance' to inspect the employee's current balances.
  2. Call 'search_company_policy' to verify policy limits and submission requirements.
  3. Perform mathematical reasoning (e.g., Annual WFA limit - WFA days used = allowable WFA days remaining).
  4. Synthesize a structured, clear response addressing each part of the user's inquiry.
- Always reply in professional, friendly English.
"""

# Golden Queries & Document Definitions imported from shared_corpus_metadata
import sys
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))

from shared_corpus_metadata import (
    DOCUMENTS_ID,
    DOCUMENTS_EN,
    GOLDEN_QUERIES_ID,
    GOLDEN_QUERIES_EN,
)

GOLDEN_QUERIES = GOLDEN_QUERIES_ID


