#!/usr/bin/env python3
"""
ingest.py — Pipeline Ingesti, Chunking, Firestore Upload, dan Vector Upsert
Membaca PDF, memecah chunk, mengunggah payload teks ke Cloud Firestore,
menghasilkan vektor embedding gemini-embedding-2, dan meng-upsert ke MatchingEngineIndex.
"""

import json
import logging
import re
import sys
import time
from pathlib import Path
import pypdf
from rich.console import Console

from google import genai
from google.genai import types
from google.cloud import aiplatform
from google.cloud import firestore
from google.cloud.aiplatform_v1.types import IndexDatapoint

from config import (
    PROJECT_ID,
    LOCATION,
    INDEX_DISPLAY_NAME,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_LOCATION,
    DOC_PREFIX,
    FIRESTORE_COLLECTION,
    FIRESTORE_DATABASE,
    SOURCE_DOCS_DIR,
    CHUNKS_CACHE_FILE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from manage_index import find_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest")
console = Console()


def clean_id(text: str) -> str:
    """Sanitizes text to alphanumeric and hyphens for chunk IDs."""
    cleaned = re.sub(r"[^a-zA-Z0-9-]", "-", text).strip("-")
    return re.sub(r"-+", "-", cleaned).lower()


def parse_and_chunk_documents(force_reparse: bool = False) -> list[dict]:
    """Parses Indonesian HR policy PDFs and extracts chunks with sliding window overlap."""
    if not force_reparse and CHUNKS_CACHE_FILE.exists():
        console.print(f"[green]Memuat chunk dari berkas cache:[/green] {CHUNKS_CACHE_FILE}")
        with open(CHUNKS_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    if not SOURCE_DOCS_DIR.exists():
        raise FileNotFoundError(f"Folder dokumen sumber tidak ditemukan: {SOURCE_DOCS_DIR}")

    pdf_files = sorted(SOURCE_DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Tidak ada berkas PDF ditemukan di: {SOURCE_DOCS_DIR}")

    chunks = []
    console.print(f"[bold yellow]Mengekstrak teks dari {len(pdf_files)} berkas PDF...[/bold yellow]")

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

        console.print(f"  • {pdf_path.name}: {len(reader.pages)} halaman, {doc_chunk_count} chunk")

    with open(CHUNKS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    console.print(f"[bold green]Total {len(chunks)} chunk disimpan ke cache:[/bold green] {CHUNKS_CACHE_FILE}")

    return chunks


def upload_chunks_to_firestore(chunks: list[dict]):
    """Uploads document chunks and text metadata to Google Cloud Firestore."""
    console.print(f"[bold yellow]Menyimpan {len(chunks)} chunk ke Cloud Firestore ({FIRESTORE_COLLECTION})...[/bold yellow]")
    db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE)
    batch = db.batch()
    batch_count = 0
    total_uploaded = 0

    for chunk in chunks:
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(chunk["chunk_id"])
        batch.set(doc_ref, {
            "chunk_id": chunk["chunk_id"],
            "source_doc": chunk["source_doc"],
            "page_num": chunk["page_num"],
            "text": chunk["text"],
            "updated_at": firestore.SERVER_TIMESTAMP,
        })
        batch_count += 1

        # Firestore commit limit is 500 operations per batch
        if batch_count >= 400:
            batch.commit()
            total_uploaded += batch_count
            console.print(f"  ✓ Berhasil mengunggah batch: {total_uploaded}/{len(chunks)}")
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()
        total_uploaded += batch_count
        console.print(f"  ✓ Berhasil mengunggah batch akhir: {total_uploaded}/{len(chunks)}")

    console.print(f"[bold green]Seluruh {total_uploaded} chunk tersimpan di Firestore![/bold green]")


def generate_embeddings(chunks: list[dict]) -> list[list[float]]:
    """Generates 768-dimensional embeddings using gemini-embedding-2."""
    console.print(f"[bold yellow]Menghasilkan embedding gemini-embedding-2 untuk {len(chunks)} chunk...[/bold yellow]")
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=EMBEDDING_LOCATION)
    cfg = types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)

    all_embeddings = []
    total = len(chunks)

    for i, c in enumerate(chunks, 1):
        content_text = DOC_PREFIX.format(source_doc=c["source_doc"], text=c["text"])
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=content_text,
            config=cfg,
        )
        emb_values = response.embeddings[0].values
        all_embeddings.append(emb_values)

        if i % 5 == 0 or i == total:
            console.print(f"  ✓ Embedding terproses: {i}/{total}")
        time.sleep(0.05)  # subtle rate-limiting protection

    return all_embeddings


def upsert_to_matching_engine(chunks: list[dict], embeddings: list[list[float]]):
    """Upserts datapoints to the MatchingEngineIndex via stream update."""
    index = find_index()
    if not index:
        console.print("[bold red]Index Matching Engine belum dibuat! Jalankan `python manage_index.py create-index` terlebih dahulu.[/bold red]")
        sys.exit(1)

    console.print(f"[bold yellow]Meng-upsert {len(chunks)} datapoints ke MatchingEngineIndex '{INDEX_DISPLAY_NAME}'...[/bold yellow]")

    datapoints = []
    for chunk, emb in zip(chunks, embeddings):
        dp = IndexDatapoint(
            datapoint_id=chunk["chunk_id"],
            feature_vector=emb,
        )
        datapoints.append(dp)

    # Upsert in batches of 100
    batch_size = 100
    total = len(datapoints)
    for i in range(0, total, batch_size):
        batch = datapoints[i:i + batch_size]
        logger.info("Upserting datapoints %d..%d to index %s...", i + 1, min(i + batch_size, total), index.display_name)
        index.upsert_datapoints(datapoints=batch)
        console.print(f"  ✓ Datapoints ter-upsert: {min(i + batch_size, total)}/{total}")

    console.print(f"[bold green]Sukses meng-upsert {total} datapoints ke Matching Engine Index![/bold green]")


def main():
    console.print("[bold cyan]=== Mulai Pipeline Ingesti Skenario 1 (Vector Search 1.0) ===[/bold cyan]\n")

    # 1. Parse & Chunk
    chunks = parse_and_chunk_documents()

    # 2. Upload to Firestore
    upload_chunks_to_firestore(chunks)

    # 3. Generate Embeddings
    embeddings = generate_embeddings(chunks)

    # 4. Upsert to Matching Engine Index
    upsert_to_matching_engine(chunks, embeddings)

    console.print("\n[bold green]Pipeline Ingesti Selesai dengan Sukses![/bold green]")


if __name__ == "__main__":
    main()
