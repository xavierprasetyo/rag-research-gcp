# HR FAQ Agent — Global (English) Version

The same HR FAQ assistant built five ways on Google Cloud, to show the trade-off between control and managed convenience at each level of abstraction. The demo does not rank the scenarios. See [PRD.md](PRD.md) for the full design.

The Bahasa Indonesia version, with its own localized dataset, is in [../indonesia-version](../indonesia-version/README.md).

## Folder Structure

| Folder | Scenario | What We Build vs. What Google Manages |
| :--- | :--- | :--- |
| [01-vector-search-1.0](01-vector-search-1.0/) | Vector Search (1.0) | We build parsing, chunking, embedding, a chunk-text store, and prompting; Google hosts the ANN index and endpoint |
| [02-agent-retrieval](02-agent-retrieval/) | Agent Retrieval (formerly Vector Search 2.0) | We build parsing, chunking, and prompting; Google stores payload + vectors and auto-embeds |
| [03-rag-engine](03-rag-engine/) | RAG Engine | We configure the corpus and call Gemini; Google parses, chunks, embeds, and stores |
| [04-agent-search-api](04-agent-search-api/) | Agent Search: Search & Answer API | We make one API call; Google runs the whole pipeline and writes the answer |
| [05-agent-search-adk](05-agent-search-adk/) | Agent Search + ADK Agent | We build the agent and HR action tools; Google manages the data store and retrieval |
| [source-documents](source-documents/) | Shared dataset | The 4 "Cymbal Corp HR Policy Suite" PDFs used by all scenarios |

## Shared Defaults

| Setting | Value |
| :--- | :--- |
| LLM | `gemini-3.8-flash` |
| Embeddings | `gemini-embedding-2` (Scenarios 1–2), `text-embedding-005` (Scenario 3), managed by Agent Search (Scenarios 4–5) |
| Region | `us-central1` |
| Resource suffix | `-en` |

## Golden Questions

| ID | Question | Pattern |
| :--- | :--- | :--- |
| Q1 | I just welcomed a new child—how many weeks of paid leave do primary caregivers get? | Semantic |
| Q2 | What is Form EXP-402B used for and what is the submission deadline? | Exact code / keyword |
| Q3 | Compare the family deductible and employer HSA contribution between the PPO and HDHP medical plans. | Table |
| Q4 | I'm employee EMP-1042. Can I work remotely from Japan for 15 workdays next month, and do I have enough PTO balance to take 5 extra vacation days while there? | Agentic + HR tool |

## Status

The source PDFs are in [source-documents/](source-documents/). The scenario folders are not implemented yet.

> [!WARNING]
> Scenario 1 deploys an index endpoint that is billed around the clock. Undeploy it after each demo.
