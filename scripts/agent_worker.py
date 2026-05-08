#!/usr/bin/env python3
"""
Docker Agent Worker - Each agent runs in its own container
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from crewai import Agent, Task, Crew, Process, LLM

AGENT_TASKS = {
    "orchestrator_refactor": {
        "role": "Orchestrator Refactoring Specialist",
        "goal": "Improve ai_workflows_orchestrator.py",
        "file": "cherenkov-professional/src/cherenkov/ai_workflows_orchestrator.py",
        "task": "Add exception handling and logging",
    },
    "test_enhancer": {
        "role": "Testing Expert",
        "goal": "Improve orchestration tests",
        "file": "cherenkov-professional/tests/test_ai_workflows_orchestrator.py",
        "task": "Add mocks to remove LLM dependencies",
    },
    "api_designer": {
        "role": "API Architect",
        "goal": "Design orchestration API",
        "file": "cherenkov-professional/docs/ORCHESTRATION_API.md",
        "task": "Create API documentation",
    },
    "doc_writer": {
        "role": "Technical Writer",
        "goal": "Document architecture",
        "file": "cherenkov-professional/docs/ARCHITECTURE.md",
        "task": "Write architecture docs",
    },
}


def run_agent(agent_role):
    """Run a single agent task"""
    config = AGENT_TASKS[agent_role]

    print(f"\n🤖 Agent {agent_role} starting...")
    print(f"Role: {config['role']}")
    print(f"Target: {config['file']}")

    # Get Ollama host from environment
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    llm = LLM(model="qwen2.5:3b", base_url=ollama_host)

    agent = Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=f"Expert in {config['goal']}",
        llm=llm,
        verbose=True,
    )

    task = Task(
        description=f"Work on {config['file']}: {config['task']}",
        expected_output="Concrete code changes or documentation",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)

    result = crew.kickoff()

    # Save result
    output_dir = Path("/workspace/swarm_outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{agent_role}_{timestamp}.txt"
    output_file.write_text(str(result))

    print(f"✅ Agent {agent_role} complete! Saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: agent_worker.py <agent_role>")
        sys.exit(1)

    agent_role = sys.argv[1]
    run_agent(agent_role)

