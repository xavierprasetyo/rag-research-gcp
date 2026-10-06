import json
import logging
import re
import sys
from pathlib import Path
import pypdf
from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud import vectorsearch_v1beta as vs

from config import (
    COLLECTION_ID,
    PROJECT_ID,
    LOCATION,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    TEXT_TEMPLATE,
    SOURCE_DOCS_DIR,
    CHUNKS_CACHE_FILE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest")


def get_collection_path() -> str:
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION_ID}"


def get_parent_location_path() -> str:
    return f"projects/{PROJECT_ID}/locations/{LOCATION}"


def ensure_collection(vs_client: vs.VectorSearchServiceClient) -> str:
    """Ensures that the collection exists with the required schema and auto-embeddings."""
    parent = get_parent_location_path()
    col_path = get_collection_path()

    logger.info("Checking if collection exists: %s", col_path)
    try:
        existing = vs_client.get_collection(name=col_path)
        logger.info("Collection '%s' already exists.", existing.name)
        return existing.name
    except NotFound:
        logger.info("Collection not found. Creating new collection '%s'...", COLLECTION_ID)

    request = vs.CreateCollectionRequest(
        parent=parent,
        collection_id=COLLECTION_ID,
        collection={
            "display_name": "Cymbal HR FAQ Indonesia",
            "description": "Koleksi Kebijakan HR PT Cymbal Indonesia (Auto-Embedding gemini-embedding-2)",
            "data_schema": {
                "type": "object",
                "properties": {
                    "chunk_id": {"type": "string"},
                    "source_doc": {"type": "string"},
                    "page_num": {"type": "number"},
                    "text": {"type": "string"},
                },
            },
            "vector_schema": {
                "embedding": {
                    "dense_vector": {
                        "dimensions": EMBEDDING_DIMENSIONS,
                        "vertex_embedding_config": {
                            "model_id": EMBEDDING_MODEL,
                            "text_template": TEXT_TEMPLATE,
                            "task_type": "RETRIEVAL_DOCUMENT",
                        },
                    },
                },
            },
        },
    )

    op = vs_client.create_collection(request=request)
    logger.info("Waiting for collection creation operation to complete...")
    res = op.result()
    logger.info("Collection created successfully: %s", res.name)
    return res.name


def clean_id(text: str) -> str:
    """Sanitizes text to alphanumeric and hyphens for DataObject IDs."""
    cleaned = re.sub(r"[^a-zA-Z0-9-]", "-", text).strip("-")
    return re.sub(r"-+", "-", cleaned).lower()


def parse_and_chunk_documents() -> list[dict]:
    """Parses Indonesian HR policy PDFs and extracts chunks."""
    if not SOURCE_DOCS_DIR.exists():
        raise FileNotFoundError(f"Source documents directory not found: {SOURCE_DOCS_DIR}")

    pdf_files = sorted(SOURCE_DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {SOURCE_DOCS_DIR}")

    chunks = []
    logger.info("Found %d PDF documents to parse in %s", len(pdf_files), SOURCE_DOCS_DIR)

    for pdf_path in pdf_files:
        reader = pypdf.PdfReader(str(pdf_path))
        doc_stem = clean_id(pdf_path.stem)
        doc_chunk_count = 0

        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            start = 0
            page_chunk_idx = 0

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
                    doc_chunk_count += 1

                if end >= len(page_text):
                    break
                start += (CHUNK_SIZE - CHUNK_OVERLAP)

        logger.info("Parsed '%s': %d pages, %d chunks", pdf_path.name, len(reader.pages), doc_chunk_count)

    # Save to local cache file
    with open(CHUNKS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d total chunks to cache: %s", len(chunks), CHUNKS_CACHE_FILE)

    return chunks


def ingest_data_objects(data_client: vs.DataObjectServiceClient, collection_name: str, chunks: list[dict]):
    """Ingests chunks as DataObjects into the Agent Retrieval Collection."""
    logger.info("Ingesting %d DataObjects into collection '%s'...", len(chunks), collection_name)
    success_count = 0
    updated_count = 0

    for idx, chunk in enumerate(chunks, 1):
        chunk_id = chunk["chunk_id"]
        data_obj = vs.DataObject(
            data={
                "chunk_id": chunk["chunk_id"],
                "source_doc": chunk["source_doc"],
                "page_num": chunk["page_num"],
                "text": chunk["text"],
            }
        )
        req = vs.CreateDataObjectRequest(
            parent=collection_name,
            data_object_id=chunk_id,
            data_object=data_obj,
        )

        try:
            data_client.create_data_object(request=req)
            success_count += 1
        except AlreadyExists:
            # If already exists, update it to ensure latest content
            update_req = vs.UpdateDataObjectRequest(
                data_object=vs.DataObject(
                    name=f"{collection_name}/dataObjects/{chunk_id}",
                    data=data_obj.data,
                )
            )
            data_client.update_data_object(request=update_req)
            updated_count += 1
        except Exception as e:
            logger.error("Failed to ingest chunk %s: %s", chunk_id, e)
            raise e

        if idx % 10 == 0 or idx == len(chunks):
            logger.info("Progress: %d/%d chunks processed", idx, len(chunks))

    logger.info("Ingestion complete: %d created, %d updated", success_count, updated_count)


def main():
    logger.info("Starting Ingestion Pipeline for Indonesia Agent Retrieval Demo")
    logger.info("Target Project: %s, Location: %s, Collection: %s", PROJECT_ID, LOCATION, COLLECTION_ID)

    vs_client = vs.VectorSearchServiceClient()
    data_client = vs.DataObjectServiceClient()

    collection_name = ensure_collection(vs_client)
    chunks = parse_and_chunk_documents()
    ingest_data_objects(data_client, collection_name, chunks)

    logger.info("✅ All documents successfully ingested and auto-embedded into Collection '%s'!", COLLECTION_ID)


if __name__ == "__main__":
    main()
