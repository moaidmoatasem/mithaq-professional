"""
CHERENKOV Agent Factory - Sovereign Execution Plane
Enforces the 'Read-SSOT' loop for all subordinate agents.
"""

from pathlib import Path
from typing import Any, Dict

from cherenkov.agents.micro_swarm.micro_agent import MicroAgent, MicroAgentConfig
from cherenkov.agents.micro_swarm.payload_tester import PayloadTester
from cherenkov.agents.micro_swarm.sanitization_agent import SanitizationAgent


class AgentFactory:
    """
    Sovereign Factory: Instantiates agents only if they acknowledge the C2 SSOT.
    """

    def __init__(self):
        self.ssot_path = Path("CHERENKOV_SSOT.md")
        self._verify_sovereignty()

    def _verify_sovereignty(self):
        """Mandatory check: Ensures the Execution Plane is tethered to the C2 Hub."""
        if not self.ssot_path.exists():
            raise RuntimeError(
                "SOVEREIGNTY_VIOLATION: CHERENKOV_SSOT.md not found. "
                "Agents cannot boot without architectural context from the C2 Hub."
            )

    def create_agent(self, agent_type: str, config: Dict[str, Any]) -> Any:
        """
        Creates an agent and injects the Sovereign operational laws.
        """
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
