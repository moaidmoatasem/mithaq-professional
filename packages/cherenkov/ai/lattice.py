"""LATTICE — adaptive learning bridge (TENSOR → Qdrant → TENSOR).

Wires the scan loop to the local Qdrant vector DB so each scan improves
context for the next one. All traffic stays on localhost (MEISSNER rule).
Findings are stripped through ABLATION before embedding.

Public API:
  embed_and_store(result: ScanResult) -> int   # returns vectors written
  query_similar_targets(target: str, k: int) -> list[dict]
  label_false_positive(finding_id: str) -> bool
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import httpx

from cherenkov.core.ablation.bridge import AblationBridge
from cherenkov.core.base_scanner import ScanResult

logger = logging.getLogger("cherenkov.lattice")

_QDRANT_BASE = "http://localhost:6333"
_COLLECTION = "cherenkov_findings"
_EMBED_MODEL = "nomic-embed-text"
_OLLAMA_BASE = "http://localhost:11434"

_ablation = AblationBridge()


async def _ensure_collection(client: httpx.AsyncClient) -> None:
    r = await client.get(f"{_QDRANT_BASE}/collections/{_COLLECTION}")
    if r.status_code == 404:
        await client.put(
            f"{_QDRANT_BASE}/collections/{_COLLECTION}",
            json={"vectors": {"size": 768, "distance": "Cosine"}},
        )
        logger.info("LATTICE: created Qdrant collection %s", _COLLECTION)


async def _embed(client: httpx.AsyncClient, text: str) -> list[float] | None:
    try:
        r = await client.post(
            f"{_OLLAMA_BASE}/api/embeddings",
            json={"model": _EMBED_MODEL, "prompt": text},
            timeout=10.0,
        )
        if r.status_code == 200:
            return r.json().get("embedding")
    except Exception as exc:
        logger.warning("LATTICE: embed failed: %s", exc)
    return None


def _finding_to_text(finding: dict[str, Any]) -> str:
    return f"{finding.get('title', '')} {finding.get('description', '')} {finding.get('cwe', '')}"


def _finding_id(target: str, title: str, cwe: str) -> str:
    return hashlib.sha256(f"{target}:{title}:{cwe}".encode()).hexdigest()[:16]


async def embed_and_store(result: ScanResult) -> int:
    """Embed each finding and upsert into Qdrant. Returns number of vectors written."""
    if not result.findings:
        return 0

    vectors_written = 0
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            await _ensure_collection(client)
        except Exception as exc:
            logger.warning("LATTICE: Qdrant unavailable, skipping storage: %s", exc)
            return 0

        points = []
        for finding in result.findings:
            raw = finding.model_dump()
            san = _ablation.sanitize(raw)
            if not san.success:
                logger.debug("LATTICE: finding dropped by ABLATION: %s", san.drop_reason)
                continue

            text = _finding_to_text(san.sanitized)
            vector = await _embed(client, text)
            if vector is None:
                continue

            fid = _finding_id(result.target, finding.title, finding.cwe)
            points.append(
                {
                    "id": abs(int(fid, 16)) % (2**63),
                    "vector": vector,
                    "payload": {
                        "target": result.target,
                        "scanner": result.scanner_name,
                        "title": san.sanitized.get("title", ""),
                        "severity": san.sanitized.get("severity", ""),
                        "cwe": san.sanitized.get("cwe", ""),
                        "false_positive": False,
                    },
                }
            )

        if points:
            r = await client.put(
                f"{_QDRANT_BASE}/collections/{_COLLECTION}/points",
                json={"points": points},
            )
            if r.status_code in (200, 201):
                vectors_written = len(points)
                logger.info("LATTICE: stored %d vectors for %s", vectors_written, result.target)
            else:
                logger.warning("LATTICE: upsert failed %s: %s", r.status_code, r.text[:200])

    return vectors_written


async def query_similar_targets(target: str, k: int = 5) -> list[dict]:
    """Return top-k past findings similar to the given target URL for TENSOR context."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        vector = await _embed(client, target)
        if vector is None:
            return []
        try:
            r = await client.post(
                f"{_QDRANT_BASE}/collections/{_COLLECTION}/points/search",
                json={
                    "vector": vector,
                    "limit": k,
                    "with_payload": True,
                    "filter": {"must": [{"key": "false_positive", "match": {"value": False}}]},
                },
                timeout=5.0,
            )
            if r.status_code == 200:
                hits = r.json().get("result", [])
                return [h["payload"] for h in hits]
        except Exception as exc:
            logger.warning("LATTICE: query failed: %s", exc)
    return []


async def label_false_positive(finding_id: str) -> bool:
    """Mark a stored finding as a false positive so it is excluded from future context."""
    try:
        point_id = abs(int(finding_id, 16)) % (2**63)
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{_QDRANT_BASE}/collections/{_COLLECTION}/points/payload",
                json={"payload": {"false_positive": True}, "points": [point_id]},
            )
            return r.status_code in (200, 201)
    except Exception as exc:
        logger.warning("LATTICE: label_false_positive failed: %s", exc)
    return False
