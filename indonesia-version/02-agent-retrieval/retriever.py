import json
import logging
import math
import re
import time
from pathlib import Path
from typing import Any, Optional
from google import genai
from google.genai import types
from google.cloud import vectorsearch_v1beta as vs

from config import (
    BASE_DIR,
    COLLECTION_ID,
    COLLECTION_ID_EN,
    TOP_K,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    PROJECT_ID,
    LOCATION,
    LLM_MODEL,
    LLM_LOCATION,
    SYSTEM_INSTRUCTION,
    SYSTEM_INSTRUCTION_EN,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retriever")


class AgentRetriever:
    def __init__(
        self,
        project_id: str = PROJECT_ID,
        location: str = LOCATION,
        collection_id: str = COLLECTION_ID,
        client_options: Any = None,
    ):
        self.project_id = project_id
        self.location = location
        self.collection_id = collection_id
        self.collection_path = f"projects/{project_id}/locations/{location}/collections/{collection_id}"
        self.collection_path_en = f"projects/{project_id}/locations/{location}/collections/{COLLECTION_ID_EN}"

        # Initialize Vector Search and Gemini clients
        self.client = vs.VectorSearchServiceClient(client_options=client_options)
        self.search_client = vs.DataObjectSearchServiceClient(client_options=client_options)
        self.genai_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=LLM_LOCATION,
        )
        self._last_execution_mode = "live_gcp"
        self._cached_chunks_by_corpus: dict[str, list[dict]] = {}
        self._cached_embeddings_by_corpus: dict[str, dict[str, list[float]]] = {}

    def _get_collection_path(self, corpus: str = "id") -> str:
        if corpus == "en":
            return self.collection_path_en
        return self.collection_path

    def _extract_chunk_data(self, search_result: Any) -> dict:
        """Extracts chunk fields and score from a SearchResult object."""
        do = search_result.data_object
        data = do.data

        return {
            "chunk_id": data.get("chunk_id", do.name.split("/")[-1]),
            "source_doc": data.get("source_doc", "Unknown"),
            "page_num": int(data.get("page_num", 1)),
            "text": data.get("text", ""),
            "score": getattr(search_result, "score", 0.0),
        }

    def _load_local_chunks(self, corpus: str = "id") -> list[dict]:
        norm_corpus = "en" if corpus == "en" else "id"
        if norm_corpus not in self._cached_chunks_by_corpus:
            fname = "chunks_cache_en.json" if norm_corpus == "en" else "chunks_cache.json"
            path = BASE_DIR / fname
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self._cached_chunks_by_corpus[norm_corpus] = json.load(f)
            else:
                self._cached_chunks_by_corpus[norm_corpus] = []
        return self._cached_chunks_by_corpus[norm_corpus]

    def _load_local_embeddings(self, corpus: str = "id") -> dict[str, list[float]]:
        norm_corpus = "en" if corpus == "en" else "id"
        if norm_corpus not in self._cached_embeddings_by_corpus:
            fname = "embeddings_cache_en.json" if norm_corpus == "en" else "embeddings_cache.json"
            candidates = [
                BASE_DIR / fname,
                BASE_DIR.parent / "01-vector-search-1.0" / fname,
            ]
            loaded: dict[str, list[float]] = {}
            for cand in candidates:
                if cand.exists():
                    try:
                        with open(cand, "r", encoding="utf-8") as f:
                            loaded = json.load(f)
                        break
                    except Exception:
                        pass
            self._cached_embeddings_by_corpus[norm_corpus] = loaded
        return self._cached_embeddings_by_corpus[norm_corpus]

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9_-]+", text.lower())

    def _search_local_bm25(self, query: str, top_k: int = TOP_K, corpus: str = "id") -> list[dict]:
        chunks = self._load_local_chunks(corpus=corpus)
        if not chunks:
            return []

        q_tokens = self._tokenize(query)
        if not q_tokens:
            return [dict(c, score=0.0) for c in chunks[:top_k]]

        doc_tokens_list = [self._tokenize(f"{c.get('source_doc', '')} {c.get('text', '')}") for c in chunks]
        avgdl = sum(len(dt) for dt in doc_tokens_list) / max(len(doc_tokens_list), 1)
        n_docs = len(chunks)

        df: dict[str, int] = {}
        for qt in set(q_tokens):
            df[qt] = sum(1 for dt in doc_tokens_list if qt in dt)

        k1 = 1.5
        b = 0.75
        scored = []
        for c, dt in zip(chunks, doc_tokens_list):
            dl = len(dt)
            score = 0.0
            tf_map: dict[str, int] = {}
            for t in dt:
                tf_map[t] = tf_map.get(t, 0) + 1
            for qt in q_tokens:
                tf = tf_map.get(qt, 0)
                if tf > 0:
                    idf = math.log(1.0 + (n_docs - df.get(qt, 0) + 0.5) / (df.get(qt, 0) + 0.5))
                    denom = tf + k1 * (1.0 - b + b * (dl / max(avgdl, 1.0)))
                    score += idf * ((tf * (k1 + 1.0)) / denom)
                    # Boost exact form codes / alphanumeric identifiers
                    if any(ch.isdigit() for ch in qt) and "-" in qt:
                        score += 5.0
            item = dict(c)
            item["score"] = round(score, 4)
            scored.append(item)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _search_local_semantic(self, query: str, top_k: int = TOP_K, corpus: str = "id") -> list[dict]:
        chunks = self._load_local_chunks(corpus=corpus)
        if not chunks:
            return []

        embeddings_map = self._load_local_embeddings(corpus=corpus)
        if not embeddings_map:
            return self._search_local_bm25(query=query, top_k=top_k, corpus=corpus)

        try:
            embed_resp = self.genai_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=f"task: question answering | query: {query}",
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
            )
            query_vec = embed_resp.embeddings[0].values
        except Exception as e:
            logger.warning("Embedding API fallback to BM25 for query '%s': %s", query, e)
            return self._search_local_bm25(query=query, top_k=top_k, corpus=corpus)

        scored = []
        for c in chunks:
            cid = c.get("chunk_id", "")
            vec = embeddings_map.get(cid)
            dot = sum(a * b for a, b in zip(query_vec, vec)) if vec else 0.0
            item = dict(c)
            item["score"] = round(dot, 4)
            scored.append(item)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _search_local_cache(
        self,
        query: str,
        top_k: int = TOP_K,
        search_mode: str = "hybrid",
        corpus: str = "id",
        rrf_k: int = 60,
    ) -> list[dict]:
        """Fallback local search over chunks_cache_en.json / chunks_cache.json using BM25 + Embedding RRF."""
        if search_mode == "semantic":
            return self._search_local_semantic(query=query, top_k=top_k, corpus=corpus)
        if search_mode == "text":
            return self._search_local_bm25(query=query, top_k=top_k, corpus=corpus)

        candidate_k = max(top_k * 2, 8)
        sem_results = self._search_local_semantic(query=query, top_k=candidate_k, corpus=corpus)
        text_results = self._search_local_bm25(query=query, top_k=candidate_k, corpus=corpus)

        rrf_scores: dict[str, float] = {}
        chunks_by_id: dict[str, dict] = {}

        for rank, item in enumerate(sem_results):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + (rank + 1)))
            chunks_by_id[cid] = item

        for rank, item in enumerate(text_results):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + (rank + 1)))
            if cid not in chunks_by_id:
                chunks_by_id[cid] = item

        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
        final_results = []
        for cid in sorted_cids[:top_k]:
            chunk_copy = dict(chunks_by_id[cid])
            chunk_copy["rrf_score"] = round(rrf_scores[cid], 4)
            final_results.append(chunk_copy)

        return final_results

    def search_semantic(self, query: str, top_k: int = TOP_K, corpus: str = "id") -> list[dict]:
        """Performs pure semantic search using gemini-embedding-2 auto-embeddings."""
        req = vs.SearchDataObjectsRequest(
            parent=self._get_collection_path(corpus),
            semantic_search=vs.SemanticSearch(
                search_text=query,
                search_field="embedding",
                task_type="QUESTION_ANSWERING",
                top_k=top_k,
                output_fields=vs.OutputFields(
                    data_fields=["chunk_id", "source_doc", "page_num", "text"]
                ),
            ),
        )
        resp = self.search_client.search_data_objects(request=req)
        return [self._extract_chunk_data(r) for r in resp.results]

    def search_text(self, query: str, top_k: int = TOP_K, corpus: str = "id") -> list[dict]:
        """Performs BM25 keyword text search on data fields."""
        req = vs.SearchDataObjectsRequest(
            parent=self._get_collection_path(corpus),
            text_search=vs.TextSearch(
                search_text=query,
                data_field_names=["text"],
                top_k=top_k,
                output_fields=vs.OutputFields(
                    data_fields=["chunk_id", "source_doc", "page_num", "text"]
                ),
            ),
        )
        resp = self.search_client.search_data_objects(request=req)
        return [self._extract_chunk_data(r) for r in resp.results]

    def search_hybrid(
        self,
        query: str,
        top_k: int = TOP_K,
        rrf_k: int = 60,
        corpus: str = "id",
    ) -> list[dict]:
        """Executes Hybrid Search combining Semantic and Text Search via Reciprocal Rank Fusion (RRF)."""
        # Fetch broader candidates from both channels
        candidate_k = max(top_k * 2, 8)
        sem_results = self.search_semantic(query, top_k=candidate_k, corpus=corpus)

        try:
            text_results = self.search_text(query, top_k=candidate_k, corpus=corpus)
        except Exception as e:
            logger.warning("TextSearch failed or not supported for query '%s': %s. Falling back to semantic only.", query, e)
            return sem_results[:top_k]

        # Calculate RRF scores: 1 / (rrf_k + rank)
        rrf_scores: dict[str, float] = {}
        chunks_by_id: dict[str, dict] = {}

        for rank, item in enumerate(sem_results):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + (rank + 1)))
            chunks_by_id[cid] = item

        for rank, item in enumerate(text_results):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + (rank + 1)))
            if cid not in chunks_by_id:
                chunks_by_id[cid] = item

        # Sort by fused score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        final_results = []
        for cid in sorted_cids[:top_k]:
            chunk_copy = dict(chunks_by_id[cid])
            chunk_copy["rrf_score"] = rrf_scores[cid]
            final_results.append(chunk_copy)

        return final_results

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        search_mode: str = "hybrid",
        corpus: str = "id",
        mode: Optional[str] = None,
    ) -> list[dict]:
        """Retrieves top-k chunks for the requested corpus ('id' or 'en'), with local cache fallback."""
        if isinstance(top_k, str):
            actual_mode = top_k
            actual_top_k = search_mode if isinstance(search_mode, int) else TOP_K
            top_k = actual_top_k
            search_mode = actual_mode

        effective_mode = mode if mode is not None else search_mode
        norm_corpus = "en" if corpus == "en" else "id"

        try:
            if effective_mode == "semantic":
                results = self.search_semantic(query, top_k=top_k, corpus=norm_corpus)
            elif effective_mode == "text":
                results = self.search_text(query, top_k=top_k, corpus=norm_corpus)
            else:
                results = self.search_hybrid(query, top_k=top_k, corpus=norm_corpus)

            if not results and norm_corpus == "en":
                raise RuntimeError("Empty results from hr-faq-en collection; using local cache fallback.")

            self._last_execution_mode = "live_gcp"
            return results
        except Exception as e:
            logger.warning(
                "Live collection query for corpus='%s' (%s) failed (%s); falling back to local cache.",
                norm_corpus,
                self._get_collection_path(norm_corpus),
                e,
            )
            self._last_execution_mode = "fallback_cache"
            return self._search_local_cache(
                query=query,
                top_k=top_k,
                search_mode=effective_mode,
                corpus=norm_corpus,
            )

    def search(self, query: str, mode: str = "hybrid", top_k: int = TOP_K, corpus: str = "id") -> list[dict]:
        """Unified search dispatch (backward-compatible alias for retrieve)."""
        return self.retrieve(query=query, top_k=top_k, search_mode=mode, corpus=corpus)

    def generate_answer(
        self,
        query: str,
        top_k: int = TOP_K,
        search_mode: str = "hybrid",
        corpus: str = "id",
        mode: Optional[str] = None,
    ) -> dict:
        """Retrieves matching chunks and generates a grounded response using Gemini."""
        if isinstance(top_k, str):
            actual_mode = top_k
            actual_top_k = search_mode if isinstance(search_mode, int) else TOP_K
            top_k = actual_top_k
            search_mode = actual_mode

        effective_mode = mode if mode is not None else search_mode
        norm_corpus = "en" if corpus == "en" else "id"

        t0 = time.perf_counter()
        chunks = self.retrieve(
            query=query,
            top_k=top_k,
            search_mode=effective_mode,
            corpus=norm_corpus,
        )
        execution_mode = getattr(self, "_last_execution_mode", "live_gcp")
        t1 = time.perf_counter()
        retrieval_ms = (t1 - t0) * 1000

        # Build prompt context based on corpus language
        context_parts = []
        if norm_corpus == "en":
            for idx, chunk in enumerate(chunks, 1):
                context_parts.append(
                    f"[Source {idx}: {chunk['source_doc']}, Page {chunk['page_num']} (ID: {chunk['chunk_id']})]\n"
                    f"{chunk['text']}"
                )
            context_str = "\n\n".join(context_parts)
            prompt = (
                f"Cymbal Global HR Policy Context:\n"
                f"----------------------------------------\n"
                f"{context_str}\n"
                f"----------------------------------------\n"
                f"Instructions:\n"
                f"{SYSTEM_INSTRUCTION_EN}\n\n"
                f"Employee Question: {query}\n"
                f"Answer:"
            )
            fallback_empty = "Sorry, unable to generate an answer."
        else:
            for idx, chunk in enumerate(chunks, 1):
                context_parts.append(
                    f"[Sumber {idx}: {chunk['source_doc']}, Hal {chunk['page_num']} (ID: {chunk['chunk_id']})]\n"
                    f"{chunk['text']}"
                )
            context_str = "\n\n".join(context_parts)
            prompt = (
                f"Konteks Kebijakan HR PT Cymbal Indonesia:\n"
                f"----------------------------------------\n"
                f"{context_str}\n"
                f"----------------------------------------\n"
                f"Instruksi:\n"
                f"{SYSTEM_INSTRUCTION}\n\n"
                f"Pertanyaan Karyawan: {query}\n"
                f"Jawaban:"
            )
            fallback_empty = "Maaf, tidak dapat menghasilkan jawaban."

        t2 = time.perf_counter()
        response = self.genai_client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
        )
        t3 = time.perf_counter()
        generation_ms = (t3 - t2) * 1000
        total_ms = (t3 - t0) * 1000

        answer_text = response.text.strip() if response and response.text else fallback_empty

        return {
            "query": query,
            "mode": effective_mode,
            "search_mode": effective_mode,
            "corpus": norm_corpus,
            "execution_mode": execution_mode,
            "answer": answer_text,
            "chunks": chunks,
            "retrieval_ms": round(retrieval_ms, 1),
            "generation_ms": round(generation_ms, 1),
            "total_ms": round(total_ms, 1),
        }
