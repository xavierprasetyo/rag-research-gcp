import logging
import time
from typing import Any
from google import genai
from google.cloud import vectorsearch_v1beta as vs

from config import (
    COLLECTION_ID,
    PROJECT_ID,
    LOCATION,
    LLM_MODEL,
    LLM_LOCATION,
    SYSTEM_INSTRUCTION,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retriever")


class AgentRetriever:
    def __init__(self, project_id: str = PROJECT_ID, location: str = LOCATION, collection_id: str = COLLECTION_ID):
        self.project_id = project_id
        self.location = location
        self.collection_id = collection_id
        self.collection_path = f"projects/{project_id}/locations/{location}/collections/{collection_id}"

        # Initialize Vector Search and Gemini clients
        self.search_client = vs.DataObjectSearchServiceClient()
        self.genai_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=LLM_LOCATION,
        )

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

    def search_semantic(self, query: str, top_k: int = 4) -> list[dict]:
        """Performs pure semantic search using gemini-embedding-2 auto-embeddings."""
        req = vs.SearchDataObjectsRequest(
            parent=self.collection_path,
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

    def search_text(self, query: str, top_k: int = 4) -> list[dict]:
        """Performs BM25 keyword text search on data fields."""
        req = vs.SearchDataObjectsRequest(
            parent=self.collection_path,
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

    def search_hybrid(self, query: str, top_k: int = 4, rrf_k: int = 60) -> list[dict]:
        """Executes Hybrid Search combining Semantic and Text Search via Reciprocal Rank Fusion (RRF)."""
        # Fetch broader candidates from both channels
        candidate_k = max(top_k * 2, 8)
        sem_results = self.search_semantic(query, top_k=candidate_k)

        try:
            text_results = self.search_text(query, top_k=candidate_k)
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

    def search(self, query: str, mode: str = "hybrid", top_k: int = 4) -> list[dict]:
        """Unified search dispatch."""
        if mode == "semantic":
            return self.search_semantic(query, top_k=top_k)
        elif mode == "text":
            return self.search_text(query, top_k=top_k)
        else:
            return self.search_hybrid(query, top_k=top_k)

    def generate_answer(self, query: str, mode: str = "hybrid", top_k: int = 4) -> dict:
        """Retrieves matching chunks and generates a grounded response using Gemini."""
        t0 = time.perf_counter()
        chunks = self.search(query, mode=mode, top_k=top_k)
        t1 = time.perf_counter()
        retrieval_ms = (t1 - t0) * 1000

        # Build prompt context
        context_parts = []
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

        t2 = time.perf_counter()
        response = self.genai_client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
        )
        t3 = time.perf_counter()
        generation_ms = (t3 - t2) * 1000
        total_ms = (t3 - t0) * 1000

        answer_text = response.text.strip() if response and response.text else "Maaf, tidak dapat menghasilkan jawaban."

        return {
            "query": query,
            "mode": mode,
            "answer": answer_text,
            "chunks": chunks,
            "retrieval_ms": round(retrieval_ms, 1),
            "generation_ms": round(generation_ms, 1),
            "total_ms": round(total_ms, 1),
        }
