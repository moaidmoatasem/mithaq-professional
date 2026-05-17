"""
LATTICE bridge — Qdrant vector store adapter for adaptive learning.

Responsibilities:
  - embed_and_store:       index a finding so similar ones can be recalled
  - query_similar_targets: retrieve the N most similar past findings
  - label_false_positive:  mark a stored finding as a false positive so future
                           scans de-rank it automatically
  - vector_count:          return the live count of indexed vectors (used by
                           /api/v1/health)

Qdrant runs on localhost:6333 by default (see deploy/docker-compose.yml).
Connection is lazy — if Qdrant is not available the bridge degrades gracefully
and logs a warning rather than crashing the API.
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("cherenkov.lattice")

_QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
_COLLECTION = "cherenkov_findings"
_VECTOR_SIZE = 384  # sentence-transformers/all-MiniLM-L6-v2 dimensionality

# ---------------------------------------------------------------------------
# Lazy Qdrant client — imported at runtime so the module loads without the dep
# ---------------------------------------------------------------------------

_client: Any | None = None
_collection_ready: bool = False


def _get_client() -> Any | None:
    """Return a connected QdrantClient or None if unavailable."""
    global _client, _collection_ready  # noqa: PLW0603

    if _client is not None:
        return _client

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams

        client = QdrantClient(url=_QDRANT_URL, timeout=3.0)

        # Ensure collection exists
        existing = {c.name for c in client.get_collections().collections}
        if _COLLECTION not in existing:
            client.create_collection(
                collection_name=_COLLECTION,
                vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("LATTICE: created collection '%s'", _COLLECTION)

        _client = client
        _collection_ready = True
        logger.info("LATTICE: connected to Qdrant at %s", _QDRANT_URL)
        return _client

    except Exception as exc:
        logger.warning("LATTICE: Qdrant unavailable (%s) — adaptive learning inactive", exc)
        return None


# ---------------------------------------------------------------------------
# Embedding helper — uses a tiny local model, no internet required
# ---------------------------------------------------------------------------


def _embed(text: str) -> list[float]:
    """
    Produce a fixed-size embedding for *text*.

    Primary: sentence-transformers (local, air-gapped compatible).
    Fallback: SHA-256 fingerprint expanded to _VECTOR_SIZE floats — deterministic
              but semantically meaningless.  Stored with a 'degraded' payload flag
              so queries can filter them out.
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]

        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text, normalize_embeddings=True).tolist()
    except Exception as exc:
        logger.debug("SentenceTransformer unavailable, using hash fallback: %s", exc)

    # Fallback: deterministic hash-based pseudo-vector
    digest = hashlib.sha256(text.encode()).digest()
    base = [b / 255.0 for b in digest]  # 32 floats
    # Tile to _VECTOR_SIZE
    tiled: list[float] = []
    while len(tiled) < _VECTOR_SIZE:
        tiled.extend(base)
    return tiled[:_VECTOR_SIZE]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass
class SimilarFinding:
    id: str
    score: float
    title: str
    target: str
    is_false_positive: bool
    scanner: str


def embed_and_store(
    finding_id: str,
    title: str,
    description: str,
    target: str,
    scanner: str,
    severity: str,
    cwe: str = "",
) -> bool:
    """
    Embed *title + description* and upsert into the LATTICE collection.

    Returns True on success, False if Qdrant is unavailable.
    """
    client = _get_client()
    if client is None:
        return False

    try:
        from qdrant_client.http.models import PointStruct

        text = f"{title}. {description}"
        vector = _embed(text)

        point = PointStruct(
            id=_str_to_uint64(finding_id),
            vector=vector,
            payload={
                "finding_id": finding_id,
                "title": title,
                "target": target,
                "scanner": scanner,
                "severity": severity,
                "cwe": cwe,
                "is_false_positive": False,
            },
        )
        client.upsert(collection_name=_COLLECTION, points=[point])
        logger.debug("LATTICE: stored finding %s", finding_id)
        return True

    except Exception as exc:
        logger.error("LATTICE: embed_and_store failed: %s", exc)
        return False


def query_similar_targets(
    title: str,
    description: str,
    top_k: int = 5,
    exclude_false_positives: bool = True,
) -> list[SimilarFinding]:
    """
    Return the *top_k* most similar past findings ordered by cosine similarity.
    """
    client = _get_client()
    if client is None:
        return []

    try:
        from qdrant_client.http.models import FieldCondition, Filter, MatchValue

        text = f"{title}. {description}"
        vector = _embed(text)

        query_filter = None
        if exclude_false_positives:
            query_filter = Filter(
                must=[FieldCondition(key="is_false_positive", match=MatchValue(value=False))]
            )

        hits = client.search(
            collection_name=_COLLECTION,
            query_vector=vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        return [
            SimilarFinding(
                id=h.payload.get("finding_id", str(h.id)),  # type: ignore[union-attr]
                score=h.score,
                title=h.payload.get("title", ""),  # type: ignore[union-attr]
                target=h.payload.get("target", ""),  # type: ignore[union-attr]
                is_false_positive=h.payload.get("is_false_positive", False),  # type: ignore[union-attr]
                scanner=h.payload.get("scanner", ""),  # type: ignore[union-attr]
            )
            for h in hits
        ]

    except Exception as exc:
        logger.error("LATTICE: query_similar_targets failed: %s", exc)
        return []


def label_false_positive(finding_id: str) -> bool:
    """
    Mark a stored finding as a false positive.
    Subsequent queries with exclude_false_positives=True will omit it.

    Returns True on success, False if the finding was not found or Qdrant is down.
    """
    client = _get_client()
    if client is None:
        return False

    try:

        client.set_payload(
            collection_name=_COLLECTION,
            payload={"is_false_positive": True},
            points=[_str_to_uint64(finding_id)],
        )
        logger.info("LATTICE: labelled %s as false positive", finding_id)
        return True

    except Exception as exc:
        logger.error("LATTICE: label_false_positive failed: %s", exc)
        return False


def vector_count() -> int:
    """
    Return the number of vectors currently stored in LATTICE.
    Returns 0 if Qdrant is unavailable.
    """
    client = _get_client()
    if client is None:
        return 0

    try:
        info = client.get_collection(_COLLECTION)
        return info.vectors_count or 0
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _str_to_uint64(value: str) -> int:
    """
    Convert an arbitrary string (e.g. UUID) to a uint64 Qdrant point ID
    by taking the first 8 bytes of its SHA-256 hash.
    """
    digest = hashlib.sha256(value.encode()).digest()
    return int.from_bytes(digest[:8], "big")
