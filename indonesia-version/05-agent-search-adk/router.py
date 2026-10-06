import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import (
    PROJECT_ID,
    LOCATION,
    DATA_STORE_ID,
    LLM_MODEL,
    HRIS_DB,
    HRIS_DB_EN,
    GOLDEN_QUERIES,
    GOLDEN_QUERIES_EN,
)
from agent import ADKHRAgent

router = APIRouter(tags=["Scenario 5: Agent Search + ADK"])

_agent_instance: Optional[ADKHRAgent] = None


def get_agent() -> ADKHRAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ADKHRAgent()
    return _agent_instance


class AgentQueryRequest(BaseModel):
    query: str
    employee_id: Optional[str] = "EMP-1042"
    corpus: Optional[str] = "id"


@router.get("/health")
def get_health():
    return {
        "status": "online",
        "scenario": "Scenario 5: Agent Search + ADK",
        "framework": "Google Agent Development Kit (google-adk)",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "datastore_id": DATA_STORE_ID,
        "llm_model": LLM_MODEL,
        "tools_available": ["get_employee_leave_balance", "get_employee_pto_balance", "search_company_policy"],
    }


@router.get("/status")
def get_status():
    return {
        "agent_name": "cymbal_hr_advisor",
        "tools_count": 3,
        "mock_employees_count": len(HRIS_DB),
        "llm_model": LLM_MODEL,
        "active_session": True,
    }


@router.get("/golden-queries")
def get_golden_queries(corpus: Optional[str] = "id"):
    if corpus == "en":
        return {"queries": GOLDEN_QUERIES_EN}
    return {"queries": GOLDEN_QUERIES}


@router.get("/employees")
def get_employees(corpus: Optional[str] = "id"):
    """Mengembalikan daftar karyawan mock dari database HRIS sesuai corpus."""
    if corpus == "en":
        return {"employees": list(HRIS_DB_EN.values())}
    return {"employees": list(HRIS_DB.values())}


@router.get("/benchmark")
def get_benchmark():
    eval_file = Path(__file__).parent / "eval_results.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            return {"results": json.load(f)}
    return {"results": []}


@router.post("/query")
def process_query(req: AgentQueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Pertanyaan tidak boleh kosong.")

    try:
        agent = get_agent()
        corpus = req.corpus or "id"
        result = agent.execute(query=req.query.strip(), employee_id=req.employee_id, corpus=corpus)
        response_payload = {
            **result,
            "execution_mode": result.get("execution_mode", "live_gcp"),
        }
        if "fallback_reason" in result and result["fallback_reason"] is not None:
            response_payload["fallback_reason"] = result["fallback_reason"]
        return response_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

