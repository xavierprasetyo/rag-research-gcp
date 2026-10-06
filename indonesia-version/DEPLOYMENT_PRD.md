# Product Requirements Document (PRD): Cloud Run Deployment for Cymbal HR Unified Portal

## 1. Executive Summary & Objective
Deploy the Indonesian Cymbal HR FAQ Suite (encompassing all 5 retrieval and search scenarios and the unified single-page application) to Google Cloud Run under project `rag-research-sandbox` in region `us-central1`. This provides the user with a single, highly available, secure public HTTPS URL to interactively demonstrate, evaluate, and compare all 5 scenarios.

---

## 2. Architecture & Topology

### 2.1 Deployment Target
- **Cloud Provider:** Google Cloud Platform (GCP)
- **Project ID:** `rag-research-sandbox` (Project Number: `1031440951381`)
- **Target Region:** `us-central1`
- **Service Name:** `cymbal-hr-unified-portal`
- **Serving Component:** Google Cloud Run (Fully Managed Serverless Container)
- **Container Registry:** Google Artifact Registry (`us-central1-docker.pkg.dev/rag-research-sandbox/cloud-run-source-deploy/cymbal-hr-unified-portal`) or Cloud Build automated container packing.

### 2.2 Container Packaging Strategy
- **Base Image:** `python:3.11-slim` (Lightweight, secure, and fast startup).
- **Embedded Frontend:** Pre-built production Vite bundle (`frontend/dist`) served directly by FastAPI gateway through static file mounting and SPA fallback routing.
- **Scenario Backend Isolation:** The container houses all 5 scenario directories (`01-vector-search-1.0` through `05-agent-search-adk`) and source documents, mounted dynamically by `server.py` with runtime module isolation.
- **Environment Variables:**
  - `PORT=8080` (Standard Cloud Run ingress port).
  - `GOOGLE_CLOUD_PROJECT=rag-research-sandbox`
  - `GCP_PROJECT=rag-research-sandbox`
  - `GCP_LOCATION=us-central1`
  - `DISCOVERY_ENGINE_LOCATION=global`
- **Cloud Run Sizing & Concurrency:**
  - Memory: 2 GiB
  - CPU: 2 vCPU
  - Concurrency: 80
  - Scaling: Min instances = 0 (scale to zero when idle to minimize cost), Max instances = 5.
  - Access: Public (`--allow-unauthenticated`) for demonstration and review.

---

## 3. System Requirements & Dependencies
- **FastAPI + Uvicorn:** Gateway routing and static asset serving.
- **Google Cloud SDKs:**
  - `google-cloud-aiplatform` (Vertex AI Vector Search & RAG Engine)
  - `google-cloud-discoveryengine` (Agent Search API)
  - `google-genai` & `google-adk` (Agent Development Kit Reasoning Agent)
  - `google-cloud-storage` (GCS access)
- **React Frontend Assets:** Bundled in `indonesia-version/unified-portal/frontend/dist`.

---

## 4. Verification Plan & Acceptance Criteria
1. **Container Build Verification:** Image successfully built via Cloud Build or local Dockerfile without dependency conflicts.
2. **Deployment Verification:** `gcloud run deploy` finishes with status `Ready: True` and returns a live `.run.app` HTTPS URL.
3. **API Health & Overview:**
   - `GET https://<SERVICE_URL>/api/health` returns HTTP 200 with all scenarios `{"s1": true, "s2": true, "s3": true, "s4": true, "s5": true}`.
   - `GET https://<SERVICE_URL>/api/overview` returns metadata for all 5 scenarios.
4. **Interactive UI Verification:**
   - Root URL `https://<SERVICE_URL>/` returns the single unified portal UI.
   - All 5 scenario tabs are operational.
   - Scenario 5 Rich Agent Inspector executes queries and shows reasoning traces.
