# Task: Issue #224 — Wire LATTICE (Qdrant + nomic-embed-text adaptive memory)

**Branch:** `fix/224-lattice-qdrant`
**Labels:** `priority:critical, phase-2, area:agent`
**PR must contain:** `Closes #224`

## Context files

```
packages/cherenkov/ai/         ← TENSOR / KINETIC / LATTICE connectors
packages/cherenkov/core/engine.py ← scan loop — hook point for embedding
deploy/docker-compose.yml      ← Qdrant already running on :6333
```

## Why this is P0

CHERENKOV markets adaptive learning as a differentiator. Qdrant is running but
has zero vectors. Every scan starts cold. The dual-brain value prop is inert.

## Architecture

```
scan finding
    ↓
ABLATION (strip PII/secrets)
    ↓
nomic-embed-text (Ollama :11434) → 768-dim vector
    ↓
Qdrant :6333 / collection: cherenkov_findings
    ↑
Before next scan: query top-K similar findings
    ↓
TENSOR system prompt receives past-finding context
```

## Implement

### Step 1 — Qdrant collection init

```python
# packages/cherenkov/ai/lattice.py

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import httpx

QDRANT_URL = "http://localhost:6333"
COLLECTION = "cherenkov_findings"
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text:latest"
VECTOR_SIZE = 768

class Lattice:
    def __init__(self):
        self._client = QdrantClient(url=QDRANT_URL)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        existing = [c.name for c in self._client.get_collections().collections]
        if COLLECTION not in existing:
            self._client.create_collection(
                COLLECTION,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
            return r.json()["embedding"]

    async def store(self, finding_id: str, finding_text: str, metadata: dict) -> None:
        vector = await self.embed(finding_text)
        self._client.upsert(COLLECTION, points=[{
            "id": finding_id,
            "vector": vector,
            "payload": {**metadata, "text": finding_text[:512]},
        }])

    async def recall(self, query: str, top_k: int = 3) -> list[dict]:
        vector = await self.embed(query)
        hits = self._client.search(COLLECTION, query_vector=vector, limit=top_k)
        return [h.payload for h in hits]
```

### Step 2 — Hook into scan loop (`engine.py`)

After each finding is produced, call:

```python
from cherenkov.ai.lattice import Lattice
from cherenkov.ai.ablation import ablate  # existing redactor

lattice = Lattice()

async def _post_finding(finding: Finding) -> None:
    safe_text = ablate(f"{finding.title}: {finding.description}")
    await lattice.store(
        finding_id=finding.id,
        finding_text=safe_text,
        metadata={"cwe": finding.cwe, "severity": finding.severity.value},
    )
```

### Step 3 — Seed TENSOR context before scan

```python
async def _get_lattice_context(target: str) -> str:
    past = await lattice.recall(f"scan target {target}")
    if not past:
        return ""
    lines = [f"- {p.get('text', '')[:200]}" for p in past]
    return "Past similar findings:\n" + "\n".join(lines)
```

## Unit tests

```python
# tests/unit/test_lattice.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_embed_returns_vector():
    with patch("httpx.AsyncClient") as mock_client:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"embedding": [0.1] * 768}
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)
        from cherenkov.ai.lattice import Lattice
        with patch.object(Lattice, "_ensure_collection"):
            lattice = Lattice()
            vec = await lattice.embed("test finding")
    assert len(vec) == 768
```

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_lattice.py -v

# Manual: after 3 scans, check Qdrant has vectors
curl http://localhost:6333/collections/cherenkov_findings
```
