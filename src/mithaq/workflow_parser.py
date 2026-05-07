"""
Workflow YAML Parser
Converts YAML workflow definitions into executable agent configurations
"""

import yaml
from typing import Dict, List, Any
from pathlib import Path


class WorkflowParser:
    """Parse YAML workflow files into agent configurations"""

    def __init__(self, workflow_file: str):
        self.workflow_file = Path(workflow_file)
        self.config = None

    def parse(self) -> Dict[str, Any]:
        """Parse the workflow YAML file"""
        if not self.workflow_file.exists():
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_file}")

        with open(self.workflow_file, "r") as f:
            self.config = yaml.safe_load(f)

        return self.config

    def get_agent_configs(self) -> List[Dict[str, Any]]:
        """Extract agent configurations from workflow"""
        if not self.config:
            self.parse()

        agents = self.config.get("agents", [])
        agent_configs = []

        for agent in agents:
            agent_configs.append(
                {
                    "role": agent.get("role", "unknown"),
                    "tools": agent.get("tools", []),
                    "config": agent,
                }
            )

        return agent_configs

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Extract task configurations from workflow"""
        if not self.config:
            self.parse()

        return self.config.get("tasks", [])

    def is_parallel(self) -> bool:
        """Check if workflow should execute in parallel"""
        if not self.config:
            self.parse()

        execution = self.config.get("execution", {})
        return execution.get("mode", "sequential") == "parallel"


def load_workflow(workflow_file: str) -> Dict[str, Any]:
    """
    Convenience function to load a workflow file

    Args:
        workflow_file: Path to YAML workflow file

    Returns:
        Parsed workflow configuration
    """
    parser = WorkflowParser(workflow_file)
    return parser.parse()
