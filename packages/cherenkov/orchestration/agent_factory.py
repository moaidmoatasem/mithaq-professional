"""
CHERENKOV Agent Factory - Sovereign Execution Plane
Enforces the 'Read-SSOT' loop for all subordinate agents.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from cherenkov.agents.micro_swarm.micro_agent import MicroAgent, MicroAgentConfig
from cherenkov.agents.micro_swarm.payload_tester import PayloadTester
from cherenkov.agents.micro_swarm.sanitization_agent import SanitizationAgent

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Sovereign Factory: Instantiates agents only if they acknowledge the C2 SSOT.
    """

    def __init__(self, ssot_path: str = ".agents/context.md"):
        self.ssot_path = Path(ssot_path)
        self._verify_sovereignty()

    def _verify_sovereignty(self):
        """Mandatory check: Ensures the Execution Plane is tethered to the C2 Hub."""
        if not self.ssot_path.exists():
            # Fallback to creating a stub if missing, or raise if strictly required
            logger.warning(f"SSOT file not found at {self.ssot_path}. Creating stub.")
            self.ssot_path.parent.mkdir(parents=True, exist_ok=True)
            self.ssot_path.write_text(
                "# CHERENKOV SSOT\n\nProject context goes here.", encoding="utf-8"
            )

    def create_agent(self, agent_type: str, config: Dict[str, Any]) -> Any:
        """
        Creates an agent and injects the Sovereign operational laws.
        """
        # Ensure agent state is registered in C2 Hub
        from cherenkov.core.c2_hub import default_c2_hub

        hub = default_c2_hub()

        agent_id = config.get("agent_id", f"{agent_type}-{id(config)}")
        role = config.get("role", agent_type)
        capabilities = config.get("capabilities", [])

        hub.state_store.get_or_create(agent_id, role, capabilities)

        # Inject mandatory system constraints into every agent
        config["system_constraints"] = {
            "perimeter": "MEISSNER_FAIL_CLOSED",
            "isolation": "TOKAMAK_CONFINEMENT",
            "privacy": "ABLATION_MANDATORY",
        }

        if agent_type == "sanitizer":
            return SanitizationAgent(config)
        elif agent_type == "tester":
            return PayloadTester(config)
        elif agent_type == "micro_agent":
            agent_config = MicroAgentConfig(**config)
            return MicroAgent(agent_config)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
