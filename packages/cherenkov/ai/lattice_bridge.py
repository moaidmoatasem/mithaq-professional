from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import uuid, logging

QDRANT_URL = 'http://localhost:6333'
COLLECTION = 'cherenkov_findings'

def _client(): return QdrantClient(url=QDRANT_URL, timeout=5)
def _model(): return SentenceTransformer('all-MiniLM-L6-v2')

def _ensure(client):
    try:
        client.get_collection(COLLECTION)
    except Exception:
        client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE))

async def embed_and_store(trace: dict) -> str:
    try:
        c = _client(); _ensure(c)
        v = _model().encode(str(trace.get('findings', ''))).tolist()
        pid = abs(hash(trace.get('trace_id', str(uuid.uuid4())))) % (2**53)
        c.upsert(COLLECTION, points=[PointStruct(id=pid, vector=v, payload=trace)])
        return str(pid)
    except Exception as e:
        logging.warning('LATTICE store failed: %s', e); return ''

async def query_similar_targets(target: str, limit: int = 5) -> list:
    try:
        c = _client()
        v = _model().encode(target).tolist()
        return [r.payload for r in c.search(COLLECTION, query_vector=v, limit=limit)]
    except Exception as e:
        logging.warning('LATTICE query failed: %s', e); return []

async def label_false_positive(finding_id: str) -> None:
    try:
        _client().set_payload(COLLECTION,
            payload={'is_false_positive': True}, points=[int(finding_id)])
    except Exception as e:
        logging.warning('LATTICE label failed: %s', e)
