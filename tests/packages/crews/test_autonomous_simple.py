#!/usr/bin/env python3
"""
Simple autonomous coding agent test with smaller model
"""

import os

import pytest
from crewai import LLM, Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.integration
@pytest.mark.skip(reason="CrewAI/OpenAI not in CHERENKOV stack — Ollama only")
def test_autonomous_simple():
    print("=" * 70)
    print("🤖 AUTONOMOUS CODE GENERATION TEST")
    print("=" * 70)

    local_llm = LLM(model="ollama/qwen2.5:3b", base_url="http://localhost:11434")

    coder = Agent(
        role="Security Tool Developer",
        goal="Write complete, production-ready Python security tools",
        backstory="""You are an expert security engineer who writes clean,
        executable Python code for vulnerability scanning and detection.""",
        llm=local_llm,
        verbose=True,
    )

    task = Task(
        description="""Write a complete Python script for SQL injection detection.

        Requirements:
        - Complete, executable Python code
        - Include error handling
        - Add usage examples
        - Make it production-ready

        Provide ONLY the complete code.""",
        expected_output="Complete Python SQL injection scanner with examples",
        agent=coder,
    )

    crew = Crew(agents=[coder], tasks=[task], process=Process.sequential, verbose=True)

    print("\n🚀 Starting autonomous code generation with qwen2.5:3b...\n")

    result = crew.kickoff()

    # Save output - FIXED CODE EXTRACTION
    os.makedirs("output", exist_ok=True)
    output_file = "output/sql_injection_scanner.py"

    result_str = str(result)

    # Better code extraction
    if "```python" in result_str:
        parts = result_str.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")
        else:
            code = result_str
    else:
        code = result_str

    with open(output_file, "w") as f:
        f.write(code.strip())

    print(f"\n✅ Code saved to: {output_file}")
    print("\n" + "=" * 70)
    print("GENERATED CODE:")
    print("=" * 70)
    print(code.strip())


if __name__ == "__main__":
    test_autonomous_simple()
