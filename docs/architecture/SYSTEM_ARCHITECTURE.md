# CHERENKOV System Architecture & Cognitive Routing

## 1. The Multi-Agent Swarm
CHERENKOV utilizes the `AgentGovernor` pattern to prevent context pollution and rate-limit cascades. Cognitive load is divided among specialized nodes.

| Agent Name | Arabic Translation | Underlying Engine | Role | Data Access Level |
| :--- | :--- | :--- | :--- | :--- |
| **TENSOR** | المهندس (The Strategist) | Groq Llama 3.1 8B | Cloud strategic planning & attack chain schema | Sanitized breadcrumbs only via ABLATION |
| **KINETIC**| المنفذ (The Executor) | Local Ollama (Llama 3.2 3B) | Local execution and issue triage | Full raw data access (behind MEISSNER) |
| **Tokamak** | البرهان (The Validator)| Python TOKAMAKed Engine| Proof validation and execution | Local tokamaked environment |
| **AEGIS** | الحكم (The Arbiter) | Local Llama 3.1 8B | Inter-agent arbiter & AIMD Circuit Breaker | Sanitized context |
| **LATTICE** | الحافظ (The Memory) | Qdrant + Embeddings | Memory, dialect-RAG, and CVE knowledge base| Local CVE vectors |

## 2. Arabic AI Capabilities
Standard LLMs fail in the MENA region due to diglossia and right-to-left (RTL) formatting. CHERENKOV bridges this gap natively:
* **Sequence-Tagging:** Utilizes SWEET sequence-tagging for fast Grammatical Error Correction without destroying the author's authentic voice.
* **Dialect-to-MSA RAG:** Uses syntax-aware chunking and BGE-M3 multilingual embeddings with a cross-encoder reranker to map regional dialects to formal compliance knowledge bases.
* **Layout-Aware OCR:** Decouples spatial coordinates from text to extract data from scanned Arabic PDFs without destroying complex RTL contract formatting.

## 3. Resilience & Routing
To prevent API timeouts from cascading into system collapse, the platform utilizes **Additive Increase Multiplicative Decrease (AIMD)** circuit breakers across all agent communications. 
