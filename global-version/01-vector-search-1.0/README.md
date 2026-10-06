# Scenario 1: Vector Search (1.0)

Maximum control: we build the whole RAG pipeline ourselves. Google hosts only the ANN index and endpoint. See [PRD §4, Scenario 1](../PRD.md#scenario-1-vector-search-10-matchingengineindex--indexendpoint).

| Item | Value |
| :--- | :--- |
| Resources | Index + IndexEndpoint `hr-faq-index-en`, external chunk-text store |
| Embedding | `gemini-embedding-2`, 768 dims, `global` location, document/query prefixes |
| We build | PDF parsing, chunking, embedding, chunk-text store, retrieval-to-prompt, Gemini call |
| Trade-off revealed | Full control over every step; no stored payload, so chunk text must live elsewhere |

> [!WARNING]
> The deployed IndexEndpoint bills around the clock. Undeploy it after each demo.
