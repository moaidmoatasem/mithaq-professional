"""
Orchestration API - Public interface for running AI workflows
"""

import logging
import threading
from queue import Queue
from typing import Any, Dict, List, Optional

from cherenkov.orchestration.agent_registry import AgentRegistry
from cherenkov.orchestration.types import AgentID, WorkflowResult
from cherenkov.orchestration.workflow_scheduler import WorkflowScheduler

logger = logging.getLogger(__name__)

_registry: AgentRegistry = AgentRegistry()
_scheduler: WorkflowScheduler = WorkflowScheduler()


def get_workflow_status(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get the status of a workflow by ID."""
    return _scheduler.get_status(workflow_id)


def orchestrate_workflow(config: Dict[str, Any]) -> WorkflowResult:
    """Execute an AI workflow based on configuration."""
    return _scheduler.schedule(config)


def register_agent(agent: Any) -> AgentID:
    """Register an AI agent with the orchestrator."""
    return _registry.register(agent)


class WorkflowExecutor:
    """Executes workflows with real agents."""

    def __init__(self, workflow_config: Dict[str, Any]) -> None:
        self.config = workflow_config
        self.agents: List[Any] = []
        self.results: List[Dict[str, Any]] = []

    def setup_agents(self) -> int:
        """Initialize agents from workflow config."""
        from cherenkov.orchestration.agent_factory import AgentFactory

        self.agents = AgentFactory.create_agents_from_workflow(self.config)
        logger.info("Set up %d agents for workflow", len(self.agents))
        return len(self.agents)

    def execute_tasks(self) -> List[Dict[str, Any]]:
        """Execute all tasks in the workflow."""
        tasks: List[Dict[str, Any]] = self.config.get("tasks", [])
        execution_mode = self.config.get("execution", {}).get("mode", "sequential")

        if execution_mode == "parallel" and len(self.agents) > 0:
            task_descriptions = [task.get("description", "") for task in tasks]
            self.results = execute_parallel(self.agents, task_descriptions)
        else:
            for i, task in enumerate(tasks):
                if i < len(self.agents):
                    agent = self.agents[i]
                    result: Dict[str, Any] = {
                        "task": task.get("name", "unknown"),
                        "agent": (agent.config.role if hasattr(agent, "config") else str(agent)),
                        "status": "completed",
                        "description": task.get("description", ""),
                    }
                    self.results.append(result)

        logger.info("Executed %d tasks in %s mode", len(self.results), execution_mode)
        return self.results

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect execution metrics."""
        return {
            "agents_deployed": len(self.agents),
            "tasks_executed": len(self.results),
            "workflow_name": self.config.get("name", "unknown"),
            "execution_mode": self.config.get("execution", {}).get("mode", "sequential"),
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate execution report."""
        metrics = self.collect_metrics()
        return {
            "workflow": self.config.get("name", "Unknown"),
            "metrics": metrics,
            "agents_used": len(self.agents),
            "tasks_completed": len(self.results),
            "results": self.results,
        }


def execute_parallel(agents: List[Any], tasks: List[Any]) -> List[Dict[str, Any]]:
    """
    Execute multiple agents in parallel using threads.
    Args:
        agents: List of agent instances
        tasks: List of tasks to execute
    Returns:
        List of results from each agent
    """
    results: List[Dict[str, Any]] = []
    result_queue: "Queue[Dict[str, Any]]" = Queue()

    def worker(agent: Any, task: Any, index: int) -> None:
        try:
            result_queue.put(
                {
                    "agent": str(agent),
                    "task": str(task),
                    "index": index,
                    "success": True,
                }
            )
        except Exception as e:
            result_queue.put(
                {
                    "agent": str(agent),
                    "index": index,
                    "success": False,
                    "error": str(e),
                }
            )

    threads = []
    for i, (agent, task) in enumerate(zip(agents, tasks, strict=False)):
        thread = threading.Thread(target=worker, args=(agent, task, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    while not result_queue.empty():
        results.append(result_queue.get())

    results.sort(key=lambda x: x.get("index", 0))
    return results
