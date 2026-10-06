# Scenario 2: Agent Retrieval (formerly Vector Search 2.0)

A managed vector database: Collections store the JSON payload and vector together and auto-embed on write. See [PRD §4, Scenario 2](../PRD.md#scenario-2-agent-retrieval-formerly-vector-search-20-collections--dataobjects).

| Item | Value |
| :--- | :--- |
| Resources | Collection `hr-faq-en` (`vectorsearch.googleapis.com/v1`) |
| Embedding | `gemini-embedding-2`, 768 dims, auto-embedded via `vertex_embedding_config` |
| We build | PDF parsing, chunking, prompt assembly, Gemini call |
| Trade-off revealed | No separate text store or embedding code; parsing and chunking quality is still ours |
