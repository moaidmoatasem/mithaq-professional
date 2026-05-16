#!/usr/bin/env python3
"""
Process extended overnight tasks continuously
"""

import subprocess
import time
from datetime import datetime

import yaml


def load_tasks():
    """Load tasks from extended-overnight-tasks.yaml"""
    with open("extended-overnight-tasks.yaml", "r") as f:
        return yaml.safe_load(f)


def generate_scanner(task_name, task_info):
    """Generate a single scanner using AI"""
    print(f"\n{'=' * 70}")
    print(f"🤖 Generating: {task_name}")
    print(f"   Type: {task_info.get('type', 'unknown')}")
    print(f"   Description: {task_info.get('description', 'N/A')}")
    print(f"{'=' * 70}\n")

    # Create a simple prompt for the AI
    prompt = f"""
Create a Python security scanner for cherenkov framework:

Name: {task_name}
Type: {task_info.get("type")}
Description: {task_info.get("description")}
Features: {task_info.get("features", [])}

Requirements:
1. Create file: src/cherenkov/scanners/{task_name.lower().replace(" ", "_").replace("-", "_")}_scanner.py
2. Include comprehensive docstrings
3. Add error handling
4. Make it production-ready
5. Follow cherenkov framework patterns

Generate the complete implementation now.
"""

    # Use Ollama to generate
    result = subprocess.run(
        ["ollama", "run", "qwen2.5-coder:3b", prompt],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode == 0:
        print(f"✅ Generated {task_name}")
        return True
    else:
        print(f"❌ Failed to generate {task_name}")
        return False


def main():
    """Main execution loop"""
    tasks = load_tasks()

    total_tasks = 0
    completed = 0

    # Count total tasks
    for _batch_name, task_list in tasks.items():
        if isinstance(task_list, list):
            total_tasks += len(task_list)

    print(f"📊 Total tasks to process: {total_tasks}")
    print(f"⏰ Estimated time: {total_tasks * 3} minutes (~{total_tasks * 3 / 60:.1f} hours)")
    print("")

    # Process each batch
    for batch_name, task_list in tasks.items():
        if not isinstance(task_list, list):
            continue

        print(f"\n{'#' * 70}")
        print(f"📦 BATCH: {batch_name}")
        print(f"{'#' * 70}\n")

        for task in task_list:
            try:
                task_name = task.get("name", "Unknown")
                if generate_scanner(task_name, task):
                    completed += 1

                progress = (completed / total_tasks) * 100
                print(f"\n📊 Progress: {completed}/{total_tasks} ({progress:.1f}%)")
                print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n")

                # Small delay between tasks
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error processing task: {e}")
                continue

    print(f"\n{'=' * 70}")
    print("🎉 EXTENDED DEVELOPMENT COMPLETE!")
    print(f"✅ Completed: {completed}/{total_tasks}")
    print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
