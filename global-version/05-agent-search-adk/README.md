# Scenario 5: Agent Search + ADK Agent

An ADK agent that combines Agent Search retrieval with custom HR action tools. See [PRD §4, Scenario 5](../PRD.md#scenario-5-agent-search--google-adk-vertexaisearchtool--custom-hr-tools).

| Item | Value |
| :--- | :--- |
| Resources | Data store `hr-faq-datastore-en` (shared with Scenario 4), ADK agent |
| Tools | `VertexAiSearchTool(bypass_multi_tools_limit=True)`, `get_employee_pto_balance(employee_id)` |
| We build | Agent instructions, HR tools, agent hosting |
| Trade-off revealed | Answers questions that need both policy lookup and live data (Q4); adds agent latency and more moving parts |
