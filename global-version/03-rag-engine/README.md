# Scenario 3: RAG Engine

A managed RAG pipeline: point a corpus at GCS and Google parses, chunks, embeds, and stores. See [PRD §4, Scenario 3](../PRD.md#scenario-3-vertex-ai-rag-engine-ragcorpus).

| Item | Value |
| :--- | :--- |
| Resources | RagCorpus `hr-faq-rag-en`, source `gs://my-bucket/hr-docs/en/` |
| Embedding | `text-embedding-005` (fixed for the corpus lifetime; retires April 1, 2027) |
| We build | Corpus config, Gemini call with the retrieval tool attached |
| Trade-off revealed | Little pipeline code; Gemini embedding models are not yet allowed, and the endpoint must be in the corpus region |
