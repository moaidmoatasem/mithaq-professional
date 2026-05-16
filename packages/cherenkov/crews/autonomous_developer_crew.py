"""
Autonomous Developer Crew
Agents that write, execute, and save code autonomously.
"""

import os

from crewai import LLM, Agent, Crew, Process, Task

# Configure local Ollama LLM
local_llm = LLM(
    model="ollama/qwen2.5-coder:7b",  # Using your better coding model
    base_url="http://localhost:11434",
)


class AutonomousDeveloperCrew:
    """
    Crew of agents that autonomously write and execute code.
    """

    def __init__(self):
        os.makedirs("output", exist_ok=True)

    def create_agents(self):
        """Create autonomous coding agents"""

        tool_developer = Agent(
            role="Security Tool Developer",
            goal="Write Python security tools and vulnerability scanners",
            backstory="""You are an expert security engineer who writes
            automated security testing tools. You write clean, executable
            Python code that finds vulnerabilities. When asked to write code,
            you provide complete, working Python scripts.""",
            llm=local_llm,
            allow_code_execution=True,
            verbose=True,
        )

        exploit_dev = Agent(
            role="Exploit Developer",
            goal="Write proof-of-concept exploits for vulnerabilities",
            backstory="""You are a penetration tester who writes POC exploits
            to demonstrate security vulnerabilities. You write working code
            that proves vulnerabilities exist. You always include safety
            warnings and ethical use notices.""",
            llm=local_llm,
            allow_code_execution=True,
            verbose=True,
        )

        report_gen = Agent(
            role="Security Report Generator",
            goal="Generate professional security reports from findings",
            backstory="""You create comprehensive security reports with code
            examples, vulnerability descriptions, and remediation guidance.
            You write detailed markdown reports.""",
            llm=local_llm,
            verbose=True,
        )

        return [tool_developer, exploit_dev, report_gen]

    def create_tasks(self, agents, vulnerability_type: str):
        """Create autonomous coding tasks"""

        tool_dev, exploit_dev, report_gen = agents

        scanner_task = Task(
            description=f"""Write a complete Python script that scans for {vulnerability_type}.

            Requirements:
            1. Write complete, executable Python code
            2. Include proper error handling
            3. Add detailed comments explaining each part
            4. Include usage examples
            5. Make it production-ready

            Provide the COMPLETE code, not just snippets.""",
            expected_output=f"Complete working Python scanner code for {vulnerability_type}",
            agent=tool_dev,
        )

        exploit_task = Task(
            description=f"""Write a proof-of-concept exploit demonstrating {vulnerability_type}.

            Requirements:
            1. Write complete demonstration code
            2. Include safe execution mode (no actual damage)
            3. Add clear warnings about ethical use
            4. Show how the vulnerability can be exploited
            5. Include comments explaining the attack

            Provide COMPLETE code that educators can use.""",
            expected_output=f"Complete POC exploit code for {vulnerability_type}",
            agent=exploit_dev,
            context=[scanner_task],
        )

        report_task = Task(
            description=f"""Create a comprehensive security report for {vulnerability_type}.

            Include in the markdown report:
            1. Executive summary
            2. Technical description of the vulnerability
            3. Code examples showing the vulnerability
            4. Impact assessment (Critical/High/Medium/Low)
            5. Step-by-step remediation instructions
            6. References and resources

            Make it professional and detailed.""",
            expected_output="Comprehensive markdown security report",
            agent=report_gen,
            context=[scanner_task, exploit_task],
        )

        return [scanner_task, exploit_task, report_task]

    def run(self, vulnerability_type: str = "SQL Injection"):
        """Execute the autonomous developer crew"""

        agents = self.create_agents()
        tasks = self.create_tasks(agents, vulnerability_type)

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            manager_llm=local_llm,  # ✅ CRITICAL FIX
            verbose=True,
        )

        print("\n🚀 Autonomous Developer Crew starting...")
        print(f"   Target: Writing tools for {vulnerability_type}\n")

        result = crew.kickoff()

        self._save_outputs(result, vulnerability_type)

        return result

    def _save_outputs(self, result, vuln_type: str):
        """Save crew outputs to files"""
        try:
            output_file = f"output/{vuln_type.replace(' ', '_').lower()}_complete_output.txt"
            with open(output_file, "w") as f:
                f.write(str(result))
            print(f"\n✅ Output saved to {output_file}")
        except Exception as e:
            print(f"⚠️  Error saving output: {e}")
