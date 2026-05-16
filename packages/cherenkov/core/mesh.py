import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MeshNode:
    def __init__(self, node_id: str, host: str, role: str = "worker"):
        self.node_id = node_id
        self.host = host
        self.role = role
        self.status = "ready"
        self.last_seen = datetime.now(timezone.utc)

class MeshManager:
    """
    Manages multi-node mesh discovery and distributed scan coordination.
    """
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.local_id = str(uuid.uuid4())[:8]
        
    def register_node(self, node_id: str, host: str, role: str = "worker"):
        self.nodes[node_id] = MeshNode(node_id, host, role)
        logger.info(f"Mesh: Registered node {node_id} ({host}) as {role}")
        
    def get_active_nodes(self) -> List[Dict]:
        return [
            {
                "id": n.node_id,
                "host": n.host,
                "role": n.role,
                "status": n.status,
                "last_seen": n.last_seen.isoformat()
            }
            for n in self.nodes.values()
        ]
        
    def heartbeat(self, node_id: str):
        if node_id in self.nodes:
            self.nodes[node_id].last_seen = datetime.now(timezone.utc)
            self.nodes[node_id].status = "ready"
