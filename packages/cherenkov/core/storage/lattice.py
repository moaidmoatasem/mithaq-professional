import json
import logging
from typing import Any, Dict, List, Optional
import httpx
import ollama

logger = logging.getLogger(__name__)

class LatticeBridge:
    """
    LATTICE - Sovereign Vector Intelligence Bridge.
    Integrates Cherenkov findings with a local Qdrant vector database.
    
    Axiom: All intelligence must be searchable by semantic proximity 
    to detect campaign patterns across isolated scan targets.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.collection_name = "cherenkov_findings"
        self.model = "llama3.2:3b" # Using Ollama for embeddings
        
    async def init_collection(self):
        """Create the findings collection if it doesn't exist."""
        try:
            async with httpx.AsyncClient() as client:
                # Check if exists
                r = await client.get(f"{self.base_url}/collections/{self.collection_name}")
                if r.status_code == 200:
                    return
                
                # Create
                logger.info(f"LATTICE: Creating collection '{self.collection_name}'")
                await client.put(
                    f"{self.base_url}/collections/{self.collection_name}",
                    json={
                        "vectors": {
                            "size": 3072, # Llama 3.2 embedding size (verify)
                            "distance": "Cosine"
                        }
                    }
                )
        except Exception as e:
            logger.error(f"LATTICE: Failed to init collection: {e}")

    async def embed_and_store(self, finding_id: str, content: str, metadata: Dict[str, Any]):
        """Embed content using Ollama and store in Qdrant."""
        try:
            # Generate embedding
            resp = ollama.embeddings(model=self.model, prompt=content)
            vector = resp['embedding']
            
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{self.base_url}/collections/{self.collection_name}/points",
                    json={
                        "points": [
                            {
                                "id": finding_id,
                                "vector": vector,
                                "payload": {
                                    **metadata,
                                    "content": content,
                                    "timestamp": metadata.get("timestamp") or ""
                                }
                            }
                        ]
                    }
                )
            logger.info(f"LATTICE: Stored finding {finding_id}")
        except Exception as e:
            logger.error(f"LATTICE: Failed to store finding: {e}")

    async def query_similar(self, content: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for semantically similar findings."""
        try:
            resp = ollama.embeddings(model=self.model, prompt=content)
            vector = resp['embedding']
            
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{self.base_url}/collections/{self.collection_name}/points/search",
                    json={
                        "vector": vector,
                        "limit": limit,
                        "with_payload": True
                    }
                )
                if r.status_code == 200:
                    return r.json().get("result", [])
            return []
        except Exception as e:
            logger.error(f"LATTICE: Search failed: {e}")
            return []
