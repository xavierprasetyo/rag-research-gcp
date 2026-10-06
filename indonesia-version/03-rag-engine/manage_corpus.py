"""Create / inspect / delete the RAG Engine corpus for Scenario 3 (Indonesia).

Usage:
    python manage_corpus.py create    # bucket + upload PDFs + corpus + import_files
    python manage_corpus.py status    # list corpus and imported files
    python manage_corpus.py delete    # delete corpus (add --bucket to remove bucket too)
"""
import json
import sys
import time
import warnings

warnings.filterwarnings("ignore")
import vertexai
from google.cloud import storage
from vertexai import rag

from config import (
    BUCKET_NAME, CHUNK_OVERLAP, CHUNK_SIZE, CORPUS_DISPLAY_NAME, CORPUS_STATE_FILE,
    EMBEDDING_MODEL, GCS_PREFIX, GCS_URI, LOCATION, PROJECT_ID, SOURCE_DOCS_DIR,
)

vertexai.init(project=PROJECT_ID, location=LOCATION)


def find_corpus():
    for c in rag.list_corpora():
        if c.display_name == CORPUS_DISPLAY_NAME:
            return c
    return None


def upload_docs():
    client = storage.Client(project=PROJECT_ID)
    bucket = client.lookup_bucket(BUCKET_NAME)
    if bucket is None:
        bucket = client.create_bucket(BUCKET_NAME, location=LOCATION)
        print(f"Bucket dibuat: gs://{BUCKET_NAME}")
    for pdf in sorted(SOURCE_DOCS_DIR.glob("*.pdf")):
        bucket.blob(f"{GCS_PREFIX}{pdf.name}").upload_from_filename(str(pdf))
        print(f"  upload {pdf.name}")


def ensure_serverless_mode():
    """New projects can't use Spanner mode in us-central1; Serverless is only in the v1beta1 SDK surface."""
    from google.cloud import aiplatform_v1beta1 as vb

    client = vb.VertexRagDataServiceClient(
        client_options={"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
    )
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    current = client.get_rag_engine_config(name=name)
    if "serverless" in current.rag_managed_db_config:
        return
    cfg = vb.RagEngineConfig(
        name=name,
        rag_managed_db_config=vb.RagManagedDbConfig(serverless=vb.RagManagedDbConfig.Serverless()),
    )
    client.update_rag_engine_config(request=vb.UpdateRagEngineConfigRequest(rag_engine_config=cfg)).result(timeout=300)
    print("RAG Engine dialihkan ke mode Serverless")


def create():
    ensure_serverless_mode()
    upload_docs()
    corpus = find_corpus()
    if corpus is None:
        corpus = rag.create_corpus(
            display_name=CORPUS_DISPLAY_NAME,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=rag.RagEmbeddingModelConfig(
                    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                        publisher_model=f"publishers/google/models/{EMBEDDING_MODEL}"
                    )
                )
            ),
        )
        print(f"Corpus dibuat: {corpus.name}")
    else:
        print(f"Corpus sudah ada: {corpus.name}")
    CORPUS_STATE_FILE.write_text(json.dumps({"corpus_name": corpus.name}))

    if len(list(rag.list_files(corpus_name=corpus.name))) >= len(list(SOURCE_DOCS_DIR.glob("*.pdf"))):
        print("File sudah terimpor, lewati import_files.")
        return

    t0 = time.perf_counter()
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_URI],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        ),
    )
    print(f"Import selesai dalam {time.perf_counter() - t0:.1f}s: "
          f"{resp.imported_rag_files_count} file diimpor, {resp.failed_rag_files_count} gagal")


def status():
    corpus = find_corpus()
    if corpus is None:
        print("Corpus belum ada.")
        return
    print(corpus.name, corpus.display_name)
    for f in rag.list_files(corpus_name=corpus.name):
        print(f"  {f.display_name}  ({f.name.split('/')[-1]})")


def delete(with_bucket: bool):
    corpus = find_corpus()
    if corpus:
        rag.delete_corpus(name=corpus.name)
        print(f"Corpus dihapus: {corpus.name}")
    CORPUS_STATE_FILE.unlink(missing_ok=True)
    if with_bucket:
        bucket = storage.Client(project=PROJECT_ID).lookup_bucket(BUCKET_NAME)
        if bucket:
            bucket.delete(force=True)
            print(f"Bucket dihapus: gs://{BUCKET_NAME}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "create":
        create()
    elif cmd == "status":
        status()
    elif cmd == "delete":
        delete("--bucket" in sys.argv)
    else:
        sys.exit(__doc__)
