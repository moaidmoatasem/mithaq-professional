#!/usr/bin/env python3
"""
Full 3-Agent Autonomous Developer Crew
"""

import os

from crewai import LLM, Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🤖 AUTONOMOUS DEVELOPER CREW - 3 AGENTS")
print("=" * 70)

local_llm = LLM(model="ollama/qwen2.5:3b", base_url="http://localhost:11434")

# Agent 1: Scanner Developer
scanner_dev = Agent(
    role="Vulnerability Scanner Developer",
    goal="Write production-ready vulnerability scanners",
    backstory="Expert at writing Python security scanning tools",
    llm=local_llm,
    verbose=True,
)

# Agent 2: Exploit Developer
exploit_dev = Agent(
    role="Exploit Developer",
    goal="Write safe POC exploits for educational purposes",
    backstory="Penetration tester who writes ethical POC code",
    llm=local_llm,
    verbose=True,
)

# Agent 3: Report Writer
report_writer = Agent(
    role="Security Report Writer",
    goal="Create professional security reports",
    backstory="Technical writer specializing in security documentation",
    llm=local_llm,
    verbose=True,
)

# Tasks
task1 = Task(
    description="Write a complete Python SQL injection scanner with error handling",
    expected_output="Complete Python scanner code",
    agent=scanner_dev,
)

task2 = Task(
    description="Write a safe POC SQL injection exploit for education. Include warnings about ethical use.",
    expected_output="Educational POC exploit code",
    agent=exploit_dev,
    context=[task1],
)

task3 = Task(
    description="Write a markdown security report about SQL injection with code examples",
    expected_output="Professional markdown security report",
    agent=report_writer,
    context=[task1, task2],
)

# Run crew
crew = Crew(
    agents=[scanner_dev, exploit_dev, report_writer],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    verbose=True,
)

print("\n🚀 Starting 3-agent autonomous developer crew...\n")

result = crew.kickoff()

# Save outputs
os.makedirs("output", exist_ok=True)

with open("output/autonomous_crew_output.txt", "w") as f:
    f.write(str(result))

print("\n" + "=" * 70)
print("✅ CREW COMPLETED!")
print("=" * 70)
print("\nOutput saved to: output/autonomous_crew_output.txt")
print(f"\nFinal Result:\n{result}")
