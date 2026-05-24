import os

import pytest
from crewai import LLM, Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.integration
@pytest.mark.skip(reason="CrewAI/OpenAI not in CHERENKOV stack — Ollama only")
def test_parallel_agents():
    local_llm = LLM(model="ollama/qwen2.5:3b", base_url="http://localhost:11434")

    print("=" * 70)
    print("🚀 PARALLEL AUTONOMOUS AGENTS TEST")
    print("=" * 70)

    # Create 3 independent agents
    agent1 = Agent(
        role="XSS Scanner Developer",
        goal="Write complete XSS detection code",
        backstory="Security expert specializing in cross-site scripting",
        llm=local_llm,
        verbose=True,
    )

    agent2 = Agent(
        role="CSRF Scanner Developer",
        goal="Write complete CSRF detection code",
        backstory="Web security specialist focused on CSRF attacks",
        llm=local_llm,
        verbose=True,
    )

    agent3 = Agent(
        role="Path Traversal Scanner Developer",
        goal="Write complete path traversal detection code",
        backstory="File system security expert",
        llm=local_llm,
        verbose=True,
    )

    # Create independent tasks (no dependencies = parallel execution)
    task1 = Task(
        description="Write a Python function to detect XSS vulnerabilities. Include error handling.",
        expected_output="Complete XSS scanner function",
        agent=agent1,
    )

    task2 = Task(
        description="Write a Python function to detect CSRF vulnerabilities. Include error handling.",
        expected_output="Complete CSRF scanner function",
        agent=agent2,
    )

    task3 = Task(
        description="Write a Python function to detect path traversal vulnerabilities. Include error handling.",
        expected_output="Complete path traversal scanner function",
        agent=agent3,
    )

    # OPTION 1: Sequential (one after another)
    print("\n📋 Running agents SEQUENTIALLY (one by one)...\n")

    crew_sequential = Crew(
        agents=[agent1, agent2, agent3],
        tasks=[task1, task2, task3],
        process=Process.sequential,  # Default - one at a time
        verbose=True,
    )

    result = crew_sequential.kickoff()

    # Save outputs
    os.makedirs("output/parallel_test", exist_ok=True)

    with open("output/parallel_test/scanners.txt", "w") as f:
        f.write(str(result))

    print("\n" + "=" * 70)
    print("✅ ALL AGENTS COMPLETED!")
    print("=" * 70)
    print("\nResults saved to: output/parallel_test/scanners.txt")
    print(f"\nFinal output:\n{result}")


if __name__ == "__main__":
    test_parallel_agents()
