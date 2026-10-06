import json
import logging
import os
import re
import sys
import time
from pathlib import Path
import pypdf
from google import genai
from google.genai import types
from google.cloud import firestore
from google.cloud import vectorsearch_v1beta as vs
from google.api_core.exceptions import AlreadyExists

# Configure paths
ROOT_DIR = Path(__file__).resolve().parent
ID_DOCS_DIR = ROOT_DIR / "indonesia-version" / "source-documents"
EN_DOCS_DIR = ROOT_DIR / "indonesia-version" / "source-documents-en"

S1_DIR = ROOT_DIR / "indonesia-version" / "01-vector-search-1.0"
S2_DIR = ROOT_DIR / "indonesia-version" / "02-agent-retrieval"

PROJECT_ID = "rag-research-sandbox"
LOCATION_S1 = "us-central1"
LOCATION_S2 = "us-central1"
EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768
FIRESTORE_COLLECTION = "hr-faq-chunks-id"
FIRESTORE_DATABASE = "(default)"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sync_expanded")

def clean_id(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9-]", "-", text).strip("-")
    return re.sub(r"-+", "-", cleaned).lower()

def parse_and_chunk(docs_dir: Path) -> list[dict]:
    pdf_files = sorted(docs_dir.glob("*.pdf"))
    logger.info("Found %d PDF files in %s", len(pdf_files), docs_dir)
    chunks = []
    for pdf_path in pdf_files:
        reader = pypdf.PdfReader(str(pdf_path))
        doc_stem = clean_id(pdf_path.stem)
        page_chunk_idx = 0
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            start = 0
            while start < len(page_text):
                end = min(start + CHUNK_SIZE, len(page_text))
                chunk_str = page_text[start:end].strip()
                if chunk_str:
                    chunk_id = f"{doc_stem}-p{page_idx + 1:02d}-c{page_chunk_idx + 1:02d}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "source_doc": pdf_path.name,
                        "page_num": page_idx + 1,
                        "text": chunk_str,
                    })
                    page_chunk_idx += 1
                if end >= len(page_text):
                    break
                start += (CHUNK_SIZE - CHUNK_OVERLAP)
    logger.info("Generated %d chunks from %d documents in %s", len(chunks), len(pdf_files), docs_dir.name)
    return chunks

def sync_firestore(chunks: list[dict], collection_name: str = FIRESTORE_COLLECTION):
    logger.info("Uploading %d chunks to Cloud Firestore (%s)...", len(chunks), collection_name)
    db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE)
    batch = db.batch()
    batch_count = 0
    total_uploaded = 0

    for chunk in chunks:
        doc_ref = db.collection(collection_name).document(chunk["chunk_id"])
        batch.set(doc_ref, {
            "chunk_id": chunk["chunk_id"],
            "source_doc": chunk["source_doc"],
            "page_num": chunk["page_num"],
            "text": chunk["text"],
            "updated_at": firestore.SERVER_TIMESTAMP,
        })
        batch_count += 1
        if batch_count >= 400:
            batch.commit()
            total_uploaded += batch_count
            logger.info("  Firestore batch committed: %d/%d", total_uploaded, len(chunks))
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()
        total_uploaded += batch_count
        logger.info("  Firestore final batch committed: %d/%d", total_uploaded, len(chunks))
    logger.info("✅ Finished uploading to Firestore (%s)!", collection_name)

def generate_and_cache_embeddings(chunks: list[dict], cache_path: Path):
    existing = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    missing_chunks = [c for c in chunks if c["chunk_id"] not in existing]
    logger.info("Embeddings: %d existing, %d missing in %s", len(existing), len(missing_chunks), cache_path.name)

    if missing_chunks:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        cfg = types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)
        
        for idx, c in enumerate(missing_chunks, 1):
            text_to_embed = f"Dokumen: {c['source_doc']} | Halaman: {c['page_num']}\n\n{c['text']}"
            resp = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text_to_embed,
                config=cfg,
            )
            emb = resp.embeddings[0].values
            existing[c["chunk_id"]] = emb
            if idx % 10 == 0 or idx == len(missing_chunks):
                logger.info("  Embedded %d/%d new chunks...", idx, len(missing_chunks))
            time.sleep(0.04)

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(existing, f)
        logger.info("✅ Saved %d total embeddings to %s", len(existing), cache_path)
    return existing

def sync_scenario2_collection(chunks: list[dict]):
    logger.info("Syncing %d chunks into Scenario 2 (Vector Search 2.0 / Agent Retrieval)...", len(chunks))
    data_client = vs.DataObjectServiceClient()
    collection_name = f"projects/{PROJECT_ID}/locations/{LOCATION_S2}/collections/hr-faq-id"
    created = 0
    updated = 0

    for idx, c in enumerate(chunks, 1):
        chunk_id = c["chunk_id"]
        data_obj = vs.DataObject(
            data={
                "chunk_id": chunk_id,
                "source_doc": c["source_doc"],
                "page_num": c["page_num"],
                "text": c["text"],
            }
        )
        req = vs.CreateDataObjectRequest(
            parent=collection_name,
            data_object_id=chunk_id,
            data_object=data_obj,
        )
        try:
            data_client.create_data_object(request=req)
            created += 1
        except AlreadyExists:
            update_req = vs.UpdateDataObjectRequest(
                data_object=vs.DataObject(
                    name=f"{collection_name}/dataObjects/{chunk_id}",
                    data=data_obj.data,
                )
            )
            data_client.update_data_object(request=update_req)
            updated += 1
        except Exception as e:
            logger.warning("DataObject create/update error on %s: %s", chunk_id, e)

        if idx % 20 == 0 or idx == len(chunks):
            logger.info("  S2 Ingestion progress: %d/%d (%d created, %d updated)", idx, len(chunks), created, updated)

    logger.info("✅ Scenario 2 DataObjects synced: %d created, %d updated", created, updated)

def main():
    logger.info("=== Starting Comprehensive Document Sync for 10 ID and 10 EN Policies ===")
    
    # 1. Indonesian Corpus Chunks
    id_chunks = parse_and_chunk(ID_DOCS_DIR)
    with open(S1_DIR / "chunks_cache.json", "w", encoding="utf-8") as f:
        json.dump(id_chunks, f, ensure_ascii=False, indent=2)
    with open(S2_DIR / "chunks_cache.json", "w", encoding="utf-8") as f:
        json.dump(id_chunks, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d Indonesian chunks to S1 and S2 chunks_cache.json", len(id_chunks))

    # 2. Upload Indonesian Chunks to Cloud Firestore
    sync_firestore(id_chunks, collection_name=FIRESTORE_COLLECTION)

    # 3. Generate & Cache Embeddings for S1 Indonesian Corpus
    s1_id_cache = S1_DIR / "embeddings_cache.json"
    generate_and_cache_embeddings(id_chunks, s1_id_cache)

    # 4. English Corpus Chunks
    en_chunks = parse_and_chunk(EN_DOCS_DIR)
    with open(S1_DIR / "chunks_cache_en.json", "w", encoding="utf-8") as f:
        json.dump(en_chunks, f, ensure_ascii=False, indent=2)
    with open(S2_DIR / "chunks_cache_en.json", "w", encoding="utf-8") as f:
        json.dump(en_chunks, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d English chunks to S1 and S2 chunks_cache_en.json", len(en_chunks))

    # 5. Upload English Chunks to Cloud Firestore
    sync_firestore(en_chunks, collection_name="hr-faq-chunks-en")

    # 6. Generate & Cache Embeddings for S1 English Corpus
    s1_en_cache = S1_DIR / "embeddings_cache_en.json"
    generate_and_cache_embeddings(en_chunks, s1_en_cache)

    # 7. Ingest into Scenario 2 Collection (Agent Retrieval)
    try:
        sync_scenario2_collection(id_chunks)
    except Exception as e:
        logger.warning("Scenario 2 sync error (non-fatal): %s", e)

    logger.info("=== All Expanded Document Corpora Successfully Synced! ===")

if __name__ == "__main__":
    main()
