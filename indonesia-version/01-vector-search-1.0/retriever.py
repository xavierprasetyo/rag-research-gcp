import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

from google import genai
from google.genai import types
from google.cloud import aiplatform
from google.cloud import firestore

from config import (
    PROJECT_ID,
    LOCATION,
    ENDPOINT_DISPLAY_NAME,
    DEPLOYED_INDEX_ID,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_LOCATION,
    QUERY_PREFIX,
    FIRESTORE_COLLECTION,
    FIRESTORE_COLLECTION_EN,
    FIRESTORE_DATABASE,
    TOP_K,
    LLM_MODEL,
    LLM_LOCATION,
    SYSTEM_INSTRUCTION,
    SYSTEM_INSTRUCTION_EN,
)
from manage_index import find_endpoint

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retriever")


class VS1Retriever:
    """
    Retriever untuk Skenario 1: Vector Search 1.0 (Matching Engine + External Firestore).
    Mengimplementasikan pipeline 4-tahap:
    1. Query Embedding manual via gemini-embedding-2 (location: global)
    2. Vector Search ANN via MatchingEngineIndexEndpoint.find_neighbors()
    3. Resolusi teks chunk eksternal via Cloud Firestore
    4. Grounded Synthesis via gemini-3.5-flash-lite
    """

    def __init__(
        self,
        project_id: str = PROJECT_ID,
        location: str = LOCATION,
        endpoint_display_name: str = ENDPOINT_DISPLAY_NAME,
        deployed_index_id: str = DEPLOYED_INDEX_ID,
    ):
        self.project_id = project_id
        self.location = location
        self.endpoint_display_name = endpoint_display_name
        self.deployed_index_id = deployed_index_id

        # Inisialisasi Firestore Client
        self.db = firestore.Client(project=project_id, database=FIRESTORE_DATABASE)

        # Inisialisasi GenAI Client (untuk embedding & LLM)
        self.genai_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=LLM_LOCATION,
        )

        # Inisialisasi Vertex AI SDK
        aiplatform.init(project=project_id, location=location)
        self._endpoint_cache = None
        self._cached_embeddings_by_corpus: dict[str, dict[str, list[float]]] = {}
        self._cached_chunks_by_corpus: dict[str, dict[str, dict[str, Any]]] = {}

    def get_endpoint(self, refresh: bool = False) -> Optional[aiplatform.MatchingEngineIndexEndpoint]:
        """Mengambil atau menyegarkan instance MatchingEngineIndexEndpoint."""
        if self._endpoint_cache is None or refresh:
            self._endpoint_cache = find_endpoint()
        return self._endpoint_cache

    def is_endpoint_deployed(self) -> bool:
        """Memeriksa apakah endpoint memiliki VM aktif dengan deployed index yang sesuai."""
        ep = self.get_endpoint()
        if not ep:
            return False
        is_dep = any(d.id == self.deployed_index_id for d in ep.deployed_indexes)
        if not is_dep:
            # Re-check with a fresh fetch from GCP in case it just finished deploying
            ep = self.get_endpoint(refresh=True)
            if ep:
                is_dep = any(d.id == self.deployed_index_id for d in ep.deployed_indexes)
        return is_dep

    def _get_cached_embeddings(self, corpus: str = "id") -> dict[str, list[float]]:
        """Loads and caches pre-computed vector embeddings for the requested corpus ('id' or 'en')."""
        norm_corpus = "en" if corpus == "en" else "id"
        if norm_corpus not in self._cached_embeddings_by_corpus:
            cache_filename = "embeddings_cache_en.json" if norm_corpus == "en" else "embeddings_cache.json"
            cache_path = Path(__file__).resolve().parent / cache_filename
            if cache_path.exists():
                with open(cache_path, "r", encoding="utf-8") as f:
                    self._cached_embeddings_by_corpus[norm_corpus] = json.load(f)
            else:
                self._cached_embeddings_by_corpus[norm_corpus] = {}
        return self._cached_embeddings_by_corpus[norm_corpus]

    def _get_cached_chunks_map(self, corpus: str = "id") -> dict[str, dict[str, Any]]:
        """Loads and caches local chunk metadata by chunk_id as a fallback if Firestore documents are missing."""
        norm_corpus = "en" if corpus == "en" else "id"
        if norm_corpus not in self._cached_chunks_by_corpus:
            cache_filename = "chunks_cache_en.json" if norm_corpus == "en" else "chunks_cache.json"
            cache_path = Path(__file__).resolve().parent / cache_filename
            chunk_map: dict[str, dict[str, Any]] = {}
            if cache_path.exists():
                with open(cache_path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for item in items:
                        cid = item.get("chunk_id")
                        if cid:
                            chunk_map[cid] = item
            self._cached_chunks_by_corpus[norm_corpus] = chunk_map
        return self._cached_chunks_by_corpus[norm_corpus]

    def _search_cached_vectors(
        self,
        query_vec: list[float],
        top_k: int = TOP_K,
        corpus: str = "id",
    ) -> list[dict[str, Any]]:
        """Fallback search using pre-computed embeddings when endpoint VM is not yet deployed."""
        embeddings_map = self._get_cached_embeddings(corpus=corpus)

        scores = []
        for chunk_id, vec in embeddings_map.items():
            # Dot product calculation (aligned with DOT_PRODUCT_DISTANCE)
            dot = sum(a * b for a, b in zip(query_vec, vec))
            scores.append({"id": chunk_id, "distance": dot})

        scores.sort(key=lambda x: x["distance"], reverse=True)
        return scores[:top_k]

    def retrieve(self, query: str, top_k: int = TOP_K, corpus: str = "id") -> dict[str, Any]:
        """
        Menjalankan Tahap 1, 2, dan 3:
        1. Embed Query
        2. ScaNN Search (mendapatkan hanya ID & jarak via VM Endpoint atau Fallback)
        3. Lookup teks dari Firestore berdasarkan ID (dengan fallback ke local chunks_cache)
        """
        norm_corpus = "en" if corpus == "en" else "id"
        ep = self.get_endpoint()
        is_deployed = self.is_endpoint_deployed()

        # ----------------------------------------------------
        # TAHAP 1: Query Embedding (Manual di sisi client)
        # ----------------------------------------------------
        t0 = time.perf_counter()
        query_text = QUERY_PREFIX.format(query=query)
        embed_cfg = types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)

        embed_resp = self.genai_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query_text,
            config=embed_cfg,
        )
        query_vec = embed_resp.embeddings[0].values
        t1 = time.perf_counter()
        embedding_ms = round((t1 - t0) * 1000, 1)

        # ----------------------------------------------------
        # TAHAP 2: ScaNN ANN Search (Vertex AI Matching Engine)
        # ----------------------------------------------------
        t2 = time.perf_counter()
        if is_deployed and ep and norm_corpus == "id":
            neighbors_resp = ep.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_vec],
                num_neighbors=top_k,
            )
            t3 = time.perf_counter()
            scann_ms = round((t3 - t2) * 1000, 1)
            neighbors = neighbors_resp[0] if neighbors_resp else []
            raw_datapoints = [{"id": n.id, "distance": getattr(n, "distance", 0.0)} for n in neighbors]
            execution_mode = "live_gcp"
        else:
            # Endpoint VM undeployed atau pencarian korpus EN menggunakan local vector cache
            raw_datapoints = self._search_cached_vectors(query_vec, top_k=top_k, corpus=norm_corpus)
            t3 = time.perf_counter()
            scann_ms = round((t3 - t2) * 1000, 1)
            execution_mode = "local_cache_fallback"

        # ----------------------------------------------------
        # TAHAP 3: Resolusi Teks Chunk Eksternal (Cloud Firestore)
        # Catatan: ScaNN hanya mengembalikan ID & distance!
        # Teks dokumen diambil dari Cloud Firestore (dengan fallback ke chunks_cache).
        # ----------------------------------------------------
        t4 = time.perf_counter()
        chunks = []
        firestore_collection = FIRESTORE_COLLECTION_EN if norm_corpus == "en" else FIRESTORE_COLLECTION
        local_chunk_map = self._get_cached_chunks_map(corpus=norm_corpus)

        for item in raw_datapoints:
            chunk_id = item["id"]
            distance = item["distance"]

            doc_data = None
            firestore_status = "MISSING"
            try:
                doc_ref = self.db.collection(firestore_collection).document(chunk_id)
                doc_snap = doc_ref.get()
                if doc_snap.exists:
                    doc_data = doc_snap.to_dict() or {}
                    firestore_status = "FOUND"
            except Exception as e:
                logger.warning("Firestore lookup error for %s in %s: %s", chunk_id, firestore_collection, e)

            if not doc_data and chunk_id in local_chunk_map:
                doc_data = local_chunk_map[chunk_id]
                firestore_status = "LOCAL_CACHE_FALLBACK"

            if doc_data:
                default_doc = "Unknown Document" if norm_corpus == "en" else "Dokumen Tidak Dikenal"
                chunks.append({
                    "datapoint_id": chunk_id,
                    "chunk_id": chunk_id,
                    "distance": round(distance, 4),
                    "source_doc": doc_data.get("source_doc", default_doc),
                    "page_num": int(doc_data.get("page_num", 1)),
                    "text": doc_data.get("text", ""),
                    "firestore_status": firestore_status,
                })
            else:
                missing_text = "[Text not found in Firestore]" if norm_corpus == "en" else "[Teks tidak ditemukan di Firestore]"
                chunks.append({
                    "datapoint_id": chunk_id,
                    "chunk_id": chunk_id,
                    "distance": round(distance, 4),
                    "source_doc": "Not Found",
                    "page_num": 0,
                    "text": missing_text,
                    "firestore_status": "MISSING",
                })

        t5 = time.perf_counter()
        firestore_ms = round((t5 - t4) * 1000, 1)

        return {
            "chunks": chunks,
            "raw_datapoints": raw_datapoints,
            "corpus": norm_corpus,
            "execution_mode": execution_mode,
            "is_live_vm": is_deployed and norm_corpus == "id",
            "vm_status": "DEPLOYED (Live VM Node)" if (is_deployed and norm_corpus == "id") else "UNDEPLOYED (Preview Mode)",
            "latency": {
                "embedding_ms": embedding_ms,
                "scann_ms": scann_ms,
                "firestore_ms": firestore_ms,
            },
        }

    def retrieve_chunks(self, query: str, top_k: int = TOP_K, corpus: str = "id") -> dict[str, Any]:
        """Alias for retrieve() to preserve backward compatibility."""
        return self.retrieve(query=query, top_k=top_k, corpus=corpus)

    def generate_answer(self, query: str, top_k: int = TOP_K, corpus: str = "id") -> dict[str, Any]:
        """
        Menjalankan pipeline pencarian lengkap dan mensintesis jawaban dengan Gemini.
        """
        norm_corpus = "en" if corpus == "en" else "id"
        retrieval = self.retrieve(query, top_k=top_k, corpus=norm_corpus)
        chunks = retrieval["chunks"]
        ret_latency = retrieval["latency"]

        # ----------------------------------------------------
        # TAHAP 4: Grounded Answer Synthesis (Gemini 3.5 Flash-Lite)
        # ----------------------------------------------------
        t6 = time.perf_counter()
        context_blocks = []
        if norm_corpus == "en":
            for idx, c in enumerate(chunks, 1):
                context_blocks.append(
                    f"[Source {idx}: {c['source_doc']} (Page {c['page_num']})]\n{c['text']}"
                )
            context_str = "\n\n---\n\n".join(context_blocks)
            prompt = (
                f"Use the following HR policy excerpts to answer the user's question.\n\n"
                f"POLICY EXCERPTS:\n{context_str}\n\n"
                f"USER QUESTION: {query}\n\n"
                f"INSTRUCTIONS:\n"
                f"- You are an HR policy assistant for Cymbal Global. Answer concisely and accurately in English based ONLY on the provided policy excerpts.\n"
                f"- Cite the source document filename and page number.\n"
                f"- If the information is not found in the excerpts above, state that clearly."
            )
            sys_instruction = SYSTEM_INSTRUCTION_EN
        else:
            for idx, c in enumerate(chunks, 1):
                context_blocks.append(
                    f"[Sumber {idx}: {c['source_doc']} (Halaman {c['page_num']})]\n{c['text']}"
                )
            context_str = "\n\n---\n\n".join(context_blocks)
            prompt = (
                f"Gunakan informasi kebijakan HR berikut untuk menjawab pertanyaan pengguna.\n\n"
                f"INFORMASI KEBIJAKAN:\n{context_str}\n\n"
                f"PERTANYAAN PENGGUNA: {query}\n\n"
                f"INSTRUKSI:\n"
                f"- Jawab dalam Bahasa Indonesia yang baku dan ringkas.\n"
                f"- Sebutkan nama dokumen sumber dan nomor halaman yang menjadi rujukan.\n"
                f"- Jika informasi tidak ditemukan dalam dokumen di atas, katakan dengan jelas."
            )
            sys_instruction = SYSTEM_INSTRUCTION

        gen_resp = self.genai_client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.2,
            ),
        )
        answer_text = gen_resp.text or ""
        t7 = time.perf_counter()
        llm_ms = round((t7 - t6) * 1000, 1)

        total_ms = round(
            ret_latency["embedding_ms"]
            + ret_latency["scann_ms"]
            + ret_latency["firestore_ms"]
            + llm_ms,
            1,
        )

        return {
            "query": query,
            "corpus": norm_corpus,
            "execution_mode": retrieval.get("execution_mode", "local_cache_fallback"),
            "answer": answer_text,
            "chunks": chunks,
            "raw_datapoints": retrieval["raw_datapoints"],
            "is_live_vm": retrieval.get("is_live_vm", False),
            "vm_status": retrieval.get("vm_status", "UNDEPLOYED"),
            "latency": {
                "embedding_ms": ret_latency["embedding_ms"],
                "scann_ms": ret_latency["scann_ms"],
                "firestore_ms": ret_latency["firestore_ms"],
                "llm_ms": llm_ms,
                "total_ms": total_ms,
            },
        }
