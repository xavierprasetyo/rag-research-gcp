import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    BACKEND_PORT,
    PROJECT_ID,
    LOCATION,
    DATA_STORE_ID,
    LLM_MODEL,
)
from router import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scenario5_server")

app = FastAPI(title="Cymbal HR FAQ Indonesia API — Scenario 5 Agent Search + ADK", version="5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(router, prefix="/api/s5")


@app.get("/")
def root():
    return {
        "scenario": "Scenario 5: Agent Search + Google ADK",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "datastore_id": DATA_STORE_ID,
        "llm_model": LLM_MODEL,
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
