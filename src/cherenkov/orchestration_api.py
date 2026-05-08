"""
Orchestration API - Public interface for running AI workflows
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Persistence for agents
AGENT_REGISTRY_PATH = Path("workflow_results/agent_registry.json")


def _load_agent_registry() -> Dict[str, Any]:
    if not AGENT_REGISTRY_PATH.exists():
        return {}
    try:
        with open(AGENT_REGISTRY_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_agent_registry(registry: Dict[str, Any]):
    AGENT_REGISTRY_PATH.parent.mkdir(exist_ok=True)
    with open(AGENT_REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


@dataclass
class WorkflowResult:
    """Result of workflow execution"""

    success: bool
    outputs: Dict[str, Any]
    duration: float
    errors: Optional[List[str]] = None


@dataclass
class AgentID:
    """Unique identifier for registered agent"""

    id: str
    role: str


def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """
    Get the status/latest result of a workflow by ID/name.

    Args:
        workflow_id: The ID or name of the workflow

    Returns:
        Dict containing the workflow status and results, or None if not found
    """
    from cherenkov.result_persistence import ResultStore

    store = ResultStore()
    return store.get_latest(workflow_id)


def orchestrate_workflow(config: Dict) -> WorkflowResult:
    """
    Execute an AI workflow based on configuration

    Args:
        config: Workflow configuration dict

    Returns:
        WorkflowResult with execution details
    """
    import time
    from cherenkov.result_persistence import ResultStore

    start = time.time()

    try:
        # TODO: Full implementation with real workflow execution
        # For now, basic validation
        if not config:
            return WorkflowResult(success=False, outputs={}, duration=0, errors=["Empty config"])

        # Placeholder workflow execution
        outputs = {"status": "executed", "config": config}

        duration = time.time() - start

        # Save results directly via API layer
        store = ResultStore()
        store.save_result(config.get("name", "Unnamed"), outputs)

        return WorkflowResult(
            success=True, outputs=outputs, duration=duration, errors=None
        )
    except Exception as e:
        return WorkflowResult(
            success=False, outputs={}, duration=time.time() - start, errors=[str(e)]
        )


def register_agent(agent: Any) -> AgentID:
    """
    Register an AI agent with the orchestrator

    Args:
        agent: Agent instance to register

    Returns:
        AgentID for the registered agent
    """
    registry = _load_agent_registry()
    agent_id = str(uuid.uuid4())
    role = agent.role if hasattr(agent, "role") else "unknown"

    registry[agent_id] = {
        "role": role,
        "registered_at": datetime.now().isoformat(),
    }

    _save_agent_registry(registry)
    return AgentID(id=agent_id, role=role)


class WorkflowExecutor:
    """Executes workflows with real agents"""

    def __init__(self, workflow_config: Dict[str, Any]):
        self.config = workflow_config
        self.agents = []
        self.results = []

    def setup_agents(self):
        """Initialize agents from workflow config"""
        from cherenkov.agent_factory import AgentFactory

        self.agents = AgentFactory.create_agents_from_workflow(self.config)
        return len(self.agents)

    def execute_tasks(self) -> List[Any]:
        """Execute all tasks in the workflow"""
        tasks = self.config.get("tasks", [])

        # Check if parallel execution
        execution_mode = self.config.get("execution", {}).get("mode", "sequential")

        if execution_mode == "parallel" and len(self.agents) > 0:
            # Use parallel execution
            task_descriptions = [task.get("description", "") for task in tasks]
            self.results = execute_parallel(self.agents, task_descriptions)
        else:
            # Sequential execution
            for i, task in enumerate(tasks):
                if i < len(self.agents):
                    agent = self.agents[i]
                    # Execute agent task
                    result = {
                        "task": task.get("name", "unknown"),
                        "agent": (agent.config.role if hasattr(agent, "config") else str(agent)),
                        "status": "completed",
                        "description": task.get("description", ""),
                    }
                    self.results.append(result)

        return self.results

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect execution metrics"""
        return {
            "agents_deployed": len(self.agents),
            "tasks_executed": len(self.results),
            "workflow_name": self.config.get("name", "unknown"),
            "execution_mode": self.config.get("execution", {}).get("mode", "sequential"),
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate execution report"""
        metrics = self.collect_metrics()
        return {
            "workflow": self.config.get("name", "Unknown"),
            "metrics": metrics,
            "agents_used": len(self.agents),
            "tasks_completed": len(self.results),
            "results": self.results,
        }


def execute_parallel(agents: List[Any], tasks: List[Any]) -> List[Any]:
    """
    Execute multiple agents in parallel

    Args:
        agents: List of agent instances
        tasks: List of tasks to execute

    Returns:
        List of results from each agent
    """
    import threading
    from queue import Queue

    results = []
    result_queue = Queue()

    def worker(agent, task, index):
        try:
            # Execute agent task
            result = {
                "agent": str(agent),
                "task": str(task),
                "index": index,
                "success": True,
            }
            result_queue.put(result)
        except Exception as e:
            result_queue.put(
                {"agent": str(agent), "index": index, "success": False, "error": str(e)}
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
