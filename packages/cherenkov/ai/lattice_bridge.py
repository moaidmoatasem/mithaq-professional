async def embed_and_store(trace: dict) -> str:
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    client = QdrantClient(url="http://localhost:6333")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    text = str(trace.get("findings", ""))
    vector = model.encode(text).tolist()
    import uuid

    from qdrant_client.models import PointStruct

    point_id = str(uuid.uuid4())
    client.upsert(
        "cherenkov_findings",
        points=[PointStruct(id=point_id[:8].replace("-", "")[:8], vector=vector, payload=trace)],
    )
    return point_id


async def query_similar_targets(target: str, limit: int = 5) -> list:
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    client = QdrantClient(url="http://localhost:6333")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vector = model.encode(target).tolist()
    try:
        results = client.search("cherenkov_findings", query_vector=vector, limit=limit)
        return [r.payload for r in results]
    except Exception:
        return []


async def label_false_positive(finding_id: str) -> None:
    from qdrant_client import QdrantClient

    client = QdrantClient(url="http://localhost:6333")
    try:
        client.set_payload(
            "cherenkov_findings", payload={"is_false_positive": True}, points=[finding_id]
        )
    except Exception:
        pass
