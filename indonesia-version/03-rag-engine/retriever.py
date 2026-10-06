import json
import logging
import time
import warnings

warnings.filterwarnings("ignore")
import vertexai
from google import genai
from google.genai import types
from vertexai import rag

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CORPUS_DISPLAY_NAME,
    CORPUS_STATE_FILE,
    EMBEDDING_MODEL,
    LLM_LOCATION,
    LLM_MODEL,
    LOCATION,
    PROJECT_ID,
    SIMILARITY_TOP_K,
    SYSTEM_INSTRUCTION,
    SYSTEM_INSTRUCTION_EN,
    TOP_K,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retriever")


def _load_corpus_name() -> str:
    return json.loads(CORPUS_STATE_FILE.read_text())["corpus_name"]


class RagEngineRetriever:
    """Two ways to use the same corpus:

    - "tool":     attach VertexRagStore to generate_content; Google retrieves and Gemini answers in one call.
    - "retrieve": call rag.retrieval_query ourselves (scores visible), then build the prompt like Scenarios 1-2.
    """

    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.corpus_name = _load_corpus_name()
        self.genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LLM_LOCATION)

    def get_corpus_info(self) -> dict:
        info = {
            "corpus_name": self.corpus_name,
            "display_name": CORPUS_DISPLAY_NAME,
            "status": "ACTIVE",
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "embedding_model": EMBEDDING_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
        }
        try:
            corpus = rag.get_corpus(name=self.corpus_name)
            if getattr(corpus, "display_name", None):
                info["display_name"] = corpus.display_name
            if getattr(corpus, "name", None):
                info["corpus_name"] = corpus.name
        except Exception as e:
            logger.warning("Could not query live RAG corpus (%s); using corpus.json metadata", e)
            if CORPUS_STATE_FILE.exists():
                try:
                    data = json.loads(CORPUS_STATE_FILE.read_text())
                    info.update(data)
                except Exception:
                    pass
        return info

    @staticmethod
    def _chunk(uri: str, title: str, text: str, score=None) -> dict:
        source = (title or uri or "Unknown").split("/")[-1]
        return {"source_doc": source, "text": text, "score": score}

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[dict]:
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=self.corpus_name)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=top_k),
        )
        return [
            self._chunk(c.source_uri, c.source_display_name, c.text, getattr(c, "score", None))
            for c in resp.contexts.contexts
        ]

    def _answer_with_tool(self, query: str, top_k: int, corpus: str = "id") -> tuple[str, list[dict], float]:
        rag_tool = types.Tool(retrieval=types.Retrieval(
            vertex_rag_store=types.VertexRagStore(
                rag_resources=[types.VertexRagStoreRagResource(rag_corpus=self.corpus_name)],
                similarity_top_k=top_k,
            )
        ))
        sys_instruction = SYSTEM_INSTRUCTION_EN if corpus == "en" else SYSTEM_INSTRUCTION
        t0 = time.perf_counter()
        response = self.genai_client.models.generate_content(
            model=LLM_MODEL,
            contents=query,
            config=types.GenerateContentConfig(system_instruction=sys_instruction, tools=[rag_tool]),
        )
        total = (time.perf_counter() - t0) * 1000
        chunks = []
        cands = response.candidates or []
        meta = cands[0].grounding_metadata if cands else None
        for gc in (meta.grounding_chunks or []) if meta else []:
            rc = gc.retrieved_context
            if rc:
                chunks.append(self._chunk(rc.uri or "", rc.title or "", rc.text or ""))
        return (response.text or "").strip(), chunks, total

    def _answer_with_retrieve(self, query: str, top_k: int, corpus: str = "id") -> tuple[str, list[dict], float, float]:
        t0 = time.perf_counter()
        chunks = self.retrieve(query, top_k)
        retrieval_ms = (time.perf_counter() - t0) * 1000
        if corpus == "en":
            context = "\n\n".join(f"[Source {i}: {c['source_doc']}]\n{c['text']}" for i, c in enumerate(chunks, 1))
            prompt = (
                f"Cymbal Global HR Policy Context:\n----------------------------------------\n{context}\n"
                f"----------------------------------------\nInstructions:\n{SYSTEM_INSTRUCTION_EN}\n\n"
                f"Employee Question: {query}\nAnswer:"
            )
        else:
            context = "\n\n".join(f"[Sumber {i}: {c['source_doc']}]\n{c['text']}" for i, c in enumerate(chunks, 1))
            prompt = (
                f"Konteks Kebijakan HR PT Cymbal Indonesia:\n----------------------------------------\n{context}\n"
                f"----------------------------------------\nInstruksi:\n{SYSTEM_INSTRUCTION}\n\n"
                f"Pertanyaan Karyawan: {query}\nJawaban:"
            )
        t1 = time.perf_counter()
        response = self.genai_client.models.generate_content(model=LLM_MODEL, contents=prompt)
        generation_ms = (time.perf_counter() - t1) * 1000
        return (response.text or "").strip(), chunks, retrieval_ms, generation_ms

    def generate_answer(
        self,
        query: str,
        top_k: int = SIMILARITY_TOP_K,
        mode: str = "tool",
        corpus: str = "id",
    ) -> dict:
        if isinstance(top_k, str):
            # Support legacy positional calls generate_answer(query, mode, top_k)
            mode, top_k = top_k, (mode if isinstance(mode, int) else SIMILARITY_TOP_K)
        if mode == "retrieve":
            answer, chunks, retrieval_ms, generation_ms = self._answer_with_retrieve(query, top_k, corpus=corpus)
            total_ms = retrieval_ms + generation_ms
        else:
            mode = "tool"
            answer, chunks, total_ms = self._answer_with_tool(query, top_k, corpus=corpus)
            retrieval_ms = generation_ms = None  # retrieval happens inside the Gemini call
        fallback_msg = (
            "Sorry, unable to generate an answer."
            if corpus == "en"
            else "Maaf, tidak dapat menghasilkan jawaban."
        )
        return {
            "query": query,
            "mode": mode,
            "corpus": corpus,
            "answer": answer or fallback_msg,
            "chunks": chunks,
            "retrieval_ms": None if retrieval_ms is None else round(retrieval_ms, 1),
            "generation_ms": None if generation_ms is None else round(generation_ms, 1),
            "total_ms": round(total_ms, 1),
            "execution_mode": "live_gcp",
        }
