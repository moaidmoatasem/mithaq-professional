"""Agent Registry — manages persistent agent registration and lookup."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from cherenkov.orchestration.types import AgentID

logger = logging.getLogger(__name__)

DEFAULT_REGISTRY_PATH = Path("workflow_results/agent_registry.json")


class AgentRegistry:
    """Persistent registry for AI agent identities."""

    def __init__(self, path: Path = DEFAULT_REGISTRY_PATH) -> None:
        self._path = path
        self._registry: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._registry = {}
            return
        try:
            with open(self._path, "r") as f:
                self._registry = json.load(f)
        except Exception as e:
            logger.warning("Failed to load agent registry from %s: %s", self._path, e)
            self._registry = {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._registry, f, indent=2)

    def register(self, agent: Any) -> AgentID:
        """Register an agent and return a unique AgentID."""
        agent_id = str(uuid.uuid4())
        role = agent.role if hasattr(agent, "role") else "unknown"
        self._registry[agent_id] = {
            "role": role,
            "registered_at": datetime.now().isoformat(),
        }
        self._save()
        logger.info("Registered agent: id=%s role=%s", agent_id, role)
        return AgentID(id=agent_id, role=role)

    def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Look up a registered agent by ID."""
        return self._registry.get(agent_id)

    def list_all(self) -> Dict[str, Any]:
        """Return all registered agents."""
        return dict(self._registry)

    def count(self) -> int:
        """Return the number of registered agents."""
        return len(self._registry)
