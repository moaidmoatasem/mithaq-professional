#!/usr/bin/env python3
"""
Orchestration Mission Agent
Reads AGENT_MISSION_ORCHESTRATION.txt and works iteratively on orchestration improvements
"""

import time
from pathlib import Path
from datetime import datetime
from daqiq.core.memory_efficient_parallel import MemoryEfficientCrew

print("""
╔══════════════════════════════════════════════════════════════╗
║  🎯 ORCHESTRATION MISSION AGENT - ITERATIVE DEVELOPMENT     ║
╚══════════════════════════════════════════════════════════════╝
""")

# Paths
MISSION_FILE = Path("daqiq-professional/AGENT_MISSION_ORCHESTRATION.txt")
NOTES_FILE = Path("daqiq-professional/AGENT_NOTES_ORCHESTRATION.md")
OUTPUT_DIR = Path("orchestration_iterations")
OUTPUT_DIR.mkdir(exist_ok=True)


def log(message):
    """Log to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def read_mission():
    """Read the mission file"""
    if not MISSION_FILE.exists():
        log(f"❌ Mission file not found: {MISSION_FILE}")
        exit(1)
    return MISSION_FILE.read_text()


def read_notes():
    """Read existing notes"""
    if NOTES_FILE.exists():
        return NOTES_FILE.read_text()
    return ""


def append_notes(content):
    """Append to notes file"""
    with open(NOTES_FILE, "a") as f:
        f.write(f"\n## Iteration {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(content + "\n")


# Read mission and context
log("📖 Reading mission and context...")
mission = read_mission()
existing_notes = read_notes()

log("\n" + "=" * 70)
log("MISSION:")
log("=" * 70)
print(mission)
log("=" * 70)

# Initialize AI crew
log("\n🤖 Initializing AI crew...")
crew = MemoryEfficientCrew(model="ollama/qwen2.5:3b", batch_size=1)

# Define the iteration task
task_context = f"""
MISSION:
{mission}

EXISTING NOTES (what we've done so far):
{existing_notes if existing_notes else "This is the first iteration - no previous work yet."}

YOUR TASK FOR THIS ITERATION:
1. Check which orchestrator files exist in the codebase:
   - Look for files in daqiq-professional/src/daqiq/
   - Look for files in daqiq/core/
   - Find test files related to orchestration
2. Read ONE key file and understand its current structure
3. Propose ONE small, concrete improvement or next step
4. Document your findings

OUTPUT REQUIREMENTS (be specific and concise):
### Files Analyzed
- List which files you checked (with paths)
- Note which ones exist and which don't

### Current Understanding
- Brief summary of what you learned from reading the code

### Recommended Next Step
- ONE specific, small action for the next iteration
- Why this is the right next step

### Updated TODO List
- 3-5 items for future iterations
"""

log("\n🎯 Starting iteration...")
log("Task: Analyze codebase and propose next step")

# Execute using the correct API
agent_configs = [
    {
        "role": "Orchestration Architect",
        "goal": "Understand the current orchestration code and propose improvements",
        "backstory": "Expert in AI workflow orchestration, system design, and incremental refactoring",
    }
]

task_configs = [
    {
        "description": task_context,
        "expected_output": "Structured analysis with files checked, understanding gained, next step, and TODO list",
    }
]

start_time = time.time()
results = crew.run_parallel_batches(
    agent_configs=agent_configs, task_configs=task_configs
)
duration = time.time() - start_time

# Extract result text
result_text = str(results[0]["result"]) if results else "No output generated"

log(f"\n✅ Iteration complete! Duration: {duration:.1f}s")

# Save result
output_file = OUTPUT_DIR / f"iteration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
output_file.write_text(result_text)
log(f"📄 Saved to: {output_file}")

# Append to notes
append_notes(result_text)
log(f"📝 Updated: {NOTES_FILE}")

log("\n" + "=" * 70)
log("🎉 ITERATION COMPLETE")
log("=" * 70)
log("\nNext steps:")
log("1. Review the output file")
log("2. Review updated AGENT_NOTES_ORCHESTRATION.md")
log("3. Run this script again for the next iteration")
log("=" * 70)
