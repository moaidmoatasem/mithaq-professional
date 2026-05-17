import logging
import socket
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

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
    Uses mDNS (Zeroconf) for network discovery.
    """
    SERVICE_TYPE = "_cherenkov._tcp.local."

    def __init__(self, node_name: Optional[str] = None, port: int = 8000):
        self.nodes: Dict[str, MeshNode] = {}
        self.local_id = node_name or f"node-{str(uuid.uuid4())[:8]}"
        self.node_name = f"{self.local_id}.{self.SERVICE_TYPE}"
        self.port = port
        self.zeroconf = Zeroconf()
        self.discovered_nodes: Set[str] = set()
        
    def register_self(self):
        """Broadcast this node to the local network."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 1))
                local_ip = s.getsockname()[0]
            except Exception:
                local_ip = "127.0.0.1"
            finally:
                s.close()

            info = ServiceInfo(
                self.SERVICE_TYPE,
                self.node_name,
                addresses=[socket.inet_aton(local_ip)],
                port=self.port,
                properties={"version": "1.1.0", "node_id": self.local_id},
            )
            self.zeroconf.register_service(info)
            logger.info("Node registered as %s at %s:%d", self.node_name, local_ip, self.port)
        except Exception as e:
            logger.error("Failed to register node: %s", e)

    def discover_nodes(self, timeout: float = 2.0) -> List[str]:
        """Discover other Cherenkov nodes on the network."""
        ServiceBrowser(self.zeroconf, self.SERVICE_TYPE, handlers=[self._on_service_state_change])
        time.sleep(timeout)
        return list(self.discovered_nodes)

    def _on_service_state_change(self, zeroconf, service_type, name, state_change):
        from zeroconf import ServiceStateChange

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                address = socket.inet_ntoa(info.addresses[0])
                node_id = info.properties.get(b"node_id", b"unknown").decode()
                self.discovered_nodes.add(f"{name} ({node_id}) @ {address}:{info.port}")
                self.nodes[node_id] = MeshNode(node_id, address)
                logger.info("Node discovered: %s (%s)", name, node_id)

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

    def shutdown(self):
        """Stop broadcasting and close zeroconf."""
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()
