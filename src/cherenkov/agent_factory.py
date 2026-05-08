"""
Agent Factory - Creates agent instances from workflow configurations
"""

from typing import Dict, Any, Optional
from cherenkov.agents.micro_swarm.micro_agent import MicroAgent, MicroAgentConfig
from cherenkov.agents.micro_swarm.sanitization_agent import SanitizationAgent
from cherenkov.agents.micro_swarm.payload_tester import PayloadTester


class AgentFactory:
    """Factory for creating agents from workflow definitions"""

    # Registry of available agent types
    AGENT_TYPES = {
        "vulnerability_scanner": "VulnerabilityScanner",
        "sanitization_gatekeeper": SanitizationAgent,
        "payload_tester": PayloadTester,
        "micro_agent": MicroAgent,
    }

    @classmethod
    def create_agent(cls, role: str, config: Dict[str, Any]) -> Any:
        """
        Create an agent instance based on role

        Args:
            role: Agent role/type
            config: Configuration dict from workflow

        Returns:
            Instantiated agent
        """
        agent_class = cls.AGENT_TYPES.get(role)

        if agent_class is None:
            # Create a generic MicroAgent if no specific type found
            return cls._create_micro_agent(role, config)

        # For actual classes, instantiate them
        if isinstance(agent_class, type):
            return agent_class(config)

        # For string references, create generic agents
        return cls._create_micro_agent(role, config)

    @classmethod
    def _create_micro_agent(cls, role: str, config: Dict[str, Any]) -> MicroAgent:
        """Create a generic MicroAgent"""

        def generic_tool(context: str) -> Dict[str, Any]:
            """Generic tool function for workflow agents"""
            return {
                "role": role,
                "status": "executed",
                "config": config,
                "context": context,
            }

        agent_config = MicroAgentConfig(
            role=role,
            purpose=config.get("description", f"Execute {role} tasks"),
            tool_function=generic_tool,
        )

        return MicroAgent(agent_config)

    @classmethod
    def create_agents_from_workflow(cls, workflow_config: Dict[str, Any]) -> list:
        """
        Create all agents defined in a workflow

        Args:
            workflow_config: Parsed workflow configuration

        Returns:
            List of instantiated agents
        """
        agents = []
        agent_configs = workflow_config.get("agents", [])

        for config in agent_configs:
            role = config.get("role", "unknown")
            agent = cls.create_agent(role, config)
            agents.append(agent)

        return agents

