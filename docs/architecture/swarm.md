# Cognitive Swarm

CHERENKOV uses a multi-agent Cognitive Swarm governed by the **Agent Governor** pattern to divide cognitive load among specialized nodes.

## Agent Nodes

| Agent | Engine | Role | Data Access |
|---|---|---|---|
| **TENSOR** | Groq Llama 3.1 8B (Cloud) | Strategic planning & attack chain schema | Sanitized breadcrumbs via ABLATION |
| **KINETIC** | Ollama Llama 3.2 3B (Local) | Local execution and issue triage | Full raw data (behind MEISSNER) |
| **AEGIS** | Local Llama 3.1 8B | Inter-agent arbiter & circuit breaker | Sanitized context |
| **LATTICE** | Qdrant + Embeddings | Memory, RAG, CVE knowledge base | Local CVE vectors |

## Governance

- **AIMD Circuit Breaker** — Prevents cascading failures
- **Agent Governor** — Routes tasks, tracks state, enforces data access levels
- **Session Protocol** — End-to-end encrypted communication between nodes
