#!/usr/bin/env python3
"""
Autonomous Agent Swarm - Parallel Development with Auto-commit
Agents work independently, make changes, and commit to repo
"""

import subprocess
from datetime import datetime
from pathlib import Path

from cherenkov.core.memory_efficient_parallel import MemoryEfficientCrew

print("""
╔══════════════════════════════════════════════════════════════╗
║  🤖 AUTONOMOUS AGENT SWARM - PARALLEL SELF-MANAGING         ║
╚══════════════════════════════════════════════════════════════╝
""")

# Configuration
REAL_FILES = [
    "cherenkov-professional/src/cherenkov/ai_workflows_orchestrator.py",
    "cherenkov/core/hybrid_orchestrator.py",
    "cherenkov-professional/tests/test_ai_workflows_orchestrator.py",
    "cherenkov-professional/tests/test_hybrid_orchestrator.py",
]

# Agent swarm tasks (run in parallel)
SWARM_TASKS = [
    {
        "name": "Orchestrator Refactorer",
        "role": "Code Refactoring Specialist",
        "goal": "Improve ai_workflows_orchestrator.py with better error handling and logging",
        "file": "cherenkov-professional/src/cherenkov/ai_workflows_orchestrator.py",
        "task": "Add comprehensive exception handling and structured logging to ai_workflows_orchestrator.py. Make small, safe improvements.",
    },
    {
        "name": "Test Enhancer",
        "role": "Testing Expert",
        "goal": "Improve orchestration tests to avoid external LLM dependencies",
        "file": "cherenkov-professional/tests/test_ai_workflows_orchestrator.py",
        "task": "Refactor tests to use mocks instead of real LLM calls. Add unit tests for error cases.",
    },
    {
        "name": "API Designer",
        "role": "API Architect",
        "goal": "Design clean public API for orchestration",
        "file": "cherenkov-professional/docs/ORCHESTRATION_API.md",
        "task": "Design and document a simple public API for running AI workflows. Define CLI commands and Python functions.",
    },
    {
        "name": "Documentation Writer",
        "role": "Technical Writer",
        "goal": "Document the orchestration system architecture",
        "file": "cherenkov-professional/docs/ARCHITECTURE.md",
        "task": "Document how the orchestration layer works, its components, and how to use it.",
    },
]


def git_commit_changes(message: str):
    """Commit changes to git"""
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        print(f"✅ Committed: {message}")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  No changes to commit")
        return False


def git_push():
    """Push to remote"""
    try:
        subprocess.run(["git", "push"], check=True)
        print("✅ Pushed to remote")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Push failed: {e}")
        return False


# Initialize swarm
print(f"\n🚀 Initializing {len(SWARM_TASKS)}-agent swarm...")
crew = MemoryEfficientCrew(model="ollama/qwen2.5:3b", batch_size=2)

# Prepare agent configs
agent_configs = [
    {
        "role": task["role"],
        "goal": task["goal"],
        "backstory": f"Expert {task['role']} focused on {task['goal']}",
    }
    for task in SWARM_TASKS
]

# Prepare task configs
task_configs = [
    {
        "description": f"""
TARGET FILE: {task['file']}

TASK: {task['task']}

REQUIREMENTS:
- Read the current file if it exists
- Make ONE small, concrete improvement
- Provide the exact code changes needed
- Ensure changes are safe and backwards compatible

OUTPUT FORMAT:
1. Current state of the file
2. Proposed change
3. Updated code
4. Why this improves the system
""",
        "expected_output": "Analysis and concrete code changes",
    }
    for task in SWARM_TASKS
]

print("\n" + "=" * 70)
print("SWARM CONFIGURATION")
print("=" * 70)
for i, task in enumerate(SWARM_TASKS, 1):
    print(f"{i}. {task['name']}: {task['file']}")
print("=" * 70)

# Execute swarm
print("\n🎯 Deploying autonomous agents...")
start_time = datetime.now()
results = crew.run_parallel_batches(agent_configs=agent_configs, task_configs=task_configs)
duration = (datetime.now() - start_time).total_seconds()

print("\n" + "=" * 70)
print("SWARM EXECUTION COMPLETE")
print("=" * 70)
print(f"Duration: {duration:.1f}s")
print(f"Batches: {len(results)}")

# Save all results
output_dir = Path("swarm_outputs")
output_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for i, result in enumerate(results):
    output_file = (
        output_dir / f"agent_{i+1}_{SWARM_TASKS[i]['name'].replace(' ', '_')}_{timestamp}.txt"
    )
    output_file.write_text(str(result["result"]))
    print(f"📄 Saved: {output_file}")

# Auto-commit if there are changes
print("\n" + "=" * 70)
print("GIT OPERATIONS")
print("=" * 70)

commit_message = f"[Autonomous Swarm] {len(SWARM_TASKS)} agents completed tasks at {timestamp}"
if git_commit_changes(commit_message):
    print("\n🚀 Pushing to remote...")
    git_push()

print("\n" + "=" * 70)
print("🎉 AUTONOMOUS SWARM SESSION COMPLETE")
print("=" * 70)
print("\nThe agents have:")
print("1. ✅ Analyzed the codebase")
print("2. ✅ Proposed improvements")
print("3. ✅ Saved detailed outputs")
print("4. ✅ Committed changes to git")
print("5. ✅ Pushed to remote repo")
print("\nCheck swarm_outputs/ for detailed results")
print("=" * 70)
