import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

QDRANT_URL = "http://localhost:6333"
COLLECTION = "cherenkov_findings"
MODEL_NAME = "all-MiniLM-L6-v2"


def _get_client():
    return QdrantClient(url=QDRANT_URL)


def _get_model():
    return SentenceTransformer(MODEL_NAME)


def _ensure_collection(client):
    try:
        client.get_collection(COLLECTION)
    except Exception:
        client.create_collection(
            COLLECTION, vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )


async def embed_and_store(trace: dict) -> str:
    client = _get_client()
    _ensure_collection(client)
    model = _get_model()
    text = str(trace.get("findings", trace.get("target", "")))
    vector = model.encode(text).tolist()
    point_id = abs(hash(str(trace.get("trace_id", uuid.uuid4())))) % (2**63)
    client.upsert(COLLECTION, points=[PointStruct(id=point_id, vector=vector, payload=trace)])
    return str(point_id)


async def query_similar_targets(target: str, limit: int = 5) -> list:
    try:
        client = _get_client()
        model = _get_model()
        vector = model.encode(target).tolist()
        results = client.search(COLLECTION, query_vector=vector, limit=limit)
        return [r.payload for r in results]
    except Exception as e:
        logging.warning("LATTICE query failed: %s", e)
        return []


async def label_false_positive(finding_id: str) -> None:
    try:
        client = _get_client()
        client.set_payload(
            COLLECTION, payload={"is_false_positive": True}, points=[int(finding_id)]
        )
    except Exception as e:
        logging.warning("LATTICE label failed: %s", e)
