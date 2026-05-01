#!/usr/bin/env python3
"""
Coordinator - Waits for agents to finish, then commits and pushes
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime

print("🎯 Coordinator waiting for agents to complete...")

# Wait for all agent outputs
output_dir = Path("/workspace/swarm_outputs")
expected_agents = 4

while True:
    completed = len(list(output_dir.glob("*.txt")))
    print(f"Progress: {completed}/{expected_agents} agents completed")
    
    if completed >= expected_agents:
        break
    
    time.sleep(10)

print("\n✅ All agents completed!")

# Commit and push
try:
    subprocess.run(['git', 'add', '-A'], check=True, cwd='/workspace')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    subprocess.run(
        ['git', 'commit', '-m', f'[Autonomous Swarm] {expected_agents} agents @ {timestamp}'],
        check=True,
        cwd='/workspace'
    )
    subprocess.run(['git', 'push'], check=True, cwd='/workspace')
    print("🚀 Changes committed and pushed!")
except Exception as e:
    print(f"⚠️  Git operation failed: {e}")
