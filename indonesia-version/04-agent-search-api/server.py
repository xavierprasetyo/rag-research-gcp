import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import (
    BACKEND_PORT,
    PROJECT_ID,
    LOCATION,
    DATA_STORE_ID,
    ENGINE_ID,
)
from router import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scenario4_server")

app = FastAPI(title="Cymbal HR FAQ Indonesia API — Scenario 4 Agent Search", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the router both directly for standalone use and at /api for consistency
app.include_router(router, prefix="/api")
app.include_router(router, prefix="/api/s4")


@app.get("/")
def root():
    return {
        "scenario": "Scenario 4: Agent Search (Search & Answer API)",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "datastore_id": DATA_STORE_ID,
        "engine_id": ENGINE_ID,
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
