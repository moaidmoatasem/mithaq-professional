import logging

"""
AI Workflows Orchestrator for cherenkov.

TODO:
- Define standard interface for AI agents (input, output, context)
- Add orchestration logic for autonomous roadmap execution
- Implement logging & metrics hooks for long-running workflows
"""

from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

AgentFn = Callable[[Dict[str, Any]], Dict[str, Any]]


class AgentRegistry:
    """
    Minimal in-memory registry for AI agents participating in workflows.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, AgentFn] = {}

    def register(self, name: str, agent_fn: AgentFn) -> None:
        if name in self._agents:
            raise ValueError(f"Agent '{name}' is already registered")
        self._agents[name] = agent_fn

    def get(self, name: str) -> AgentFn:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise ValueError(f"Agent '{name}' is not registered") from exc

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())


def orchestrate_ai_workflows(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for AI workflows orchestration.

    :param context: High-level configuration and runtime context for agents.
                    Expected keys:
                      - project_name: str
                      - roadmap: list[dict] (high-level tasks/steps)
                      - agents: dict[str, AgentFn] or similar
    :return: Orchestration summary with per-step results.
    """
    # 1. Validate context
    required_keys = ["project_name", "roadmap", "agents"]
    missing = [k for k in required_keys if k not in context]
    if missing:
        raise ValueError(f"Missing required context keys: {missing}")

    project_name = context["project_name"]
    roadmap = context["roadmap"]
    agents_mapping = context["agents"]

    if not isinstance(roadmap, list):
        raise ValueError("context['roadmap'] must be a list of steps")

    if not isinstance(agents_mapping, dict):
        raise ValueError("context['agents'] must be a dict of agent callables")

    registry = AgentRegistry()

    # 2. Register agents from context
    for name, fn in agents_mapping.items():
        if not callable(fn):
            raise ValueError(f"Agent '{name}' is not callable")
        registry.register(name, fn)

    # 3. Simple run loop stub over roadmap steps
    print(f"[cherenkov-ai] Starting orchestration for project: {project_name}")

    step_results: List[Dict[str, Any]] = []

    for idx, step in enumerate(roadmap, start=1):
        step_name = step.get("name", f"step-{idx}")
        agent_name = step.get("agent")
        agent_input = step.get("input", {})

        print(f"[cherenkov-ai] Executing step {idx}: {step_name} using agent '{agent_name}'")

        result_record: Dict[str, Any] = {
            "index": idx,
            "name": step_name,
            "agent": agent_name,
            "input": agent_input,
            "status": "pending",
            "result": None,
            "error": None,
        }

        if not agent_name:
            msg = "No agent specified"
            print(f"[cherenkov-ai] Skipping step {idx}: {msg}")
            result_record["status"] = "skipped"
            result_record["error"] = msg
            step_results.append(result_record)
            continue

        try:
            agent_fn = registry.get(agent_name)
        except ValueError as exc:
            msg = str(exc)
            print(f"[cherenkov-ai] Error: {msg}")
            result_record["status"] = "error"
            result_record["error"] = msg
            step_results.append(result_record)
            continue

        try:
            output = agent_fn(agent_input)
            print(f"[cherenkov-ai] Step {idx} completed with result: {output}")
            result_record["status"] = "completed"
            result_record["result"] = output
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            print(f"[cherenkov-ai] Step {idx} failed with error: {msg}")
            result_record["status"] = "error"
            result_record["error"] = msg

        step_results.append(result_record)

    print(f"[cherenkov-ai] Orchestration finished for project: {project_name}")

    return {
        "project_name": project_name,
        "total_steps": len(roadmap),
        "steps": step_results,
    }
