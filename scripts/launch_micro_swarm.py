#!/usr/bin/env python3
"""
Launch MicroGPT Swarm - Parallel micro agents for cherenkov
"""

import sys

sys.path.insert(0, ".")

from cherenkov.agents.micro_swarm.micro_agent import MicroAgent, MicroAgentConfig
from cherenkov.agents.micro_swarm.payload_tester import test_sql_injection
from cherenkov.agents.micro_swarm.sanitization_agent import scrub_secrets
from cherenkov.agents.micro_swarm.swarm_orchestrator import MicroSwarm

print("""
╔══════════════════════════════════════════════════════════════╗
║  🐝 MICRO-GPT SWARM - RAM-EFFICIENT PARALLEL AGENTS         ║
╚══════════════════════════════════════════════════════════════╝
""")

# Create specialized micro agents
agents = [
    MicroAgent(
        MicroAgentConfig(
            role="Sanitizer",
            purpose="Scrub PII and secrets from logs",
            tool_function=scrub_secrets,
        )
    ),
    MicroAgent(
        MicroAgentConfig(
            role="PayloadTester1",
            purpose="Test SQL injection endpoint 1",
            tool_function=lambda x: test_sql_injection(x),
        )
    ),
    MicroAgent(
        MicroAgentConfig(
            role="PayloadTester2",
            purpose="Test SQL injection endpoint 2",
            tool_function=lambda x: test_sql_injection(x),
        )
    ),
    MicroAgent(
        MicroAgentConfig(
            role="PayloadTester3",
            purpose="Test SQL injection endpoint 3",
            tool_function=lambda x: test_sql_injection(x),
        )
    ),
]

# Define tasks
tasks = [
    "API_KEY=sk-1234567890abcdef User: admin@company.com Path: /home/user/secrets.txt IP: 192.168.1.100",
    "https://example.com/api/users",
    "https://example.com/api/products",
    "https://example.com/api/search",
]

# Deploy swarm
swarm = MicroSwarm(max_parallel=4)
results = swarm.deploy(agents, tasks)

# Print results
print("\n" + "=" * 70)
print("SWARM RESULTS")
print("=" * 70)
for i, result in enumerate(results, 1):
    status = "✅" if result["success"] else "❌"
    print(f"{status} Agent {i} ({result['agent']}): {result.get('duration', 0):.2f}s")
    if result["success"]:
        print(f"   Result: {str(result['result'])[:100]}...")

print("\n🎉 Micro swarm complete!")
