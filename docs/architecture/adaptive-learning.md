# Adaptive Learning

CHERENKOV learns from every scan through the **LATTICE** memory system — a local vector database that stores embeddings of past findings, attack patterns, and compliance mappings.

## How It Works

1. Scan completes → embeddings generated from findings
2. Embeddings stored in Qdrant vector DB
3. Next scan → LATTICE retrieves similar past findings via semantic search
4. TENSOR uses retrieved context to generate more targeted attack chains

## Benefits

- **Reduced false positives** — Learns which findings are real vs noise
- **Faster scans** — Prioritizes attack vectors that worked before
- **Compliance mapping** — Automatically maps findings to regulatory frameworks
- **Dialect-aware** — Supports Arabic diglossia via dialect-to-MSA RAG pipeline
