# Scenario 4: Agent Search — Search & Answer API

Turnkey search: one API call returns a grounded answer with citations. See [PRD §4, Scenario 4](../PRD.md#scenario-4-agent-search--search--answer-api-formerly-vertex-ai-search).

| Item | Value |
| :--- | :--- |
| Resources | Data store `hr-faq-datastore-en`, source `gs://my-bucket/hr-docs/en/` (shared with Scenario 5) |
| Embedding | Managed by Agent Search |
| We build | One `SearchServiceClient` call with a summary spec |
| Trade-off revealed | Hybrid search, layout parsing, and answer generation out of the box; little control over the internals |
