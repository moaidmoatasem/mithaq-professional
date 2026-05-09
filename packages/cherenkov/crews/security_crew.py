"""Security crew for multi-agent security audits."""

from typing import Any

from crewai import Crew, Process, Task

from cherenkov.agents.architect_agent import ArchitectAgent
from cherenkov.agents.developer_agent import DeveloperAgent
from cherenkov.agents.tester_agent import TesterAgent


class SecurityCrew:
    """Multi-agent security audit crew."""

    def __init__(
        self,
        architect: ArchitectAgent | None = None,
        developer: DeveloperAgent | None = None,
        tester: TesterAgent | None = None,
        process: Process = Process.sequential,
        verbose: bool = True,
    ):
        """Initialize security crew.

        Args:
            architect: Security architect agent (created if not provided)
            developer: Security developer agent (created if not provided)
            tester: Security tester agent (created if not provided)
            process: Crew process type (sequential or hierarchical)
            verbose: Enable verbose output
        """
        self.architect = architect or ArchitectAgent()
        self.developer = developer or DeveloperAgent()
        self.tester = tester or TesterAgent()
        self.process = process
        self.verbose = verbose

    def create_crew(self, tasks: list[Task]) -> Crew:
        """Create CrewAI crew with agents and tasks.

        Args:
            tasks: List of tasks to execute

        Returns:
            Configured Crew instance
        """
        return Crew(
            agents=[
                self.architect.agent,
                self.developer.agent,
                self.tester.agent,
            ],
            tasks=tasks,
            process=self.process,
            verbose=self.verbose,
        )

    def perform_security_audit(self, target: str, scope: list[str]) -> dict[str, Any]:
        """Perform complete security audit.

        Args:
            target: Target application/system
            scope: Audit scope (e.g., ["threat_model", "code_review", "pentest"])

        Returns:
            Dictionary containing audit results
        """
        tasks = []

        # Task 1: Threat modeling (Architect)
        if "threat_model" in scope:
            threat_task = Task(
                description=f"Analyze threat model for {target}",
                expected_output="STRIDE-based threat model with attack vectors",
                agent=self.architect.agent,
            )
            tasks.append(threat_task)

        # Task 2: Code review (Developer)
        if "code_review" in scope:
            code_task = Task(
                description=f"Review code security for {target}",
                expected_output="Security vulnerabilities and code issues",
                agent=self.developer.agent,
            )
            tasks.append(code_task)

        # Task 3: Penetration testing (Tester)
        if "pentest" in scope:
            pentest_task = Task(
                description=f"Perform penetration testing on {target}",
                expected_output="Validated vulnerabilities with exploitation proof",
                agent=self.tester.agent,
            )
            tasks.append(pentest_task)

        # Create and execute crew
        crew = self.create_crew(tasks)
        result = crew.kickoff()

        return {
            "target": target,
            "scope": scope,
            "result": str(result),
            "agents_used": len(tasks),
        }

    def analyze_mobile_app(self, apk_path: str) -> dict[str, Any]:
        """Analyze mobile application security.

        Args:
            apk_path: Path to APK file

        Returns:
            Mobile security analysis results
        """
        tasks = [
            Task(
                description=f"Analyze threat model for mobile app at {apk_path}",
                expected_output="Mobile-specific threat model (OWASP MASVS)",
                agent=self.architect.agent,
            ),
            Task(
                description=f"Analyze Smali bytecode from {apk_path}",
                expected_output="Reverse engineering findings and vulnerabilities",
                agent=self.developer.agent,
            ),
            Task(
                description=f"Perform mobile penetration testing on {apk_path}",
                expected_output="Exploitable vulnerabilities in mobile app",
                agent=self.tester.agent,
            ),
        ]

        crew = self.create_crew(tasks)
        result = crew.kickoff()

        return {
            "apk_path": apk_path,
            "analysis_type": "mobile_security",
            "result": str(result),
            "agents_used": 3,
        }

    def get_crew_info(self) -> dict[str, Any]:
        """Get information about crew configuration.

        Returns:
            Dictionary with crew details
        """
        return {
            "agents": {
                "architect": self.architect.config.role,
                "developer": self.developer.config.role,
                "tester": self.tester.config.role,
            },
            "process": str(self.process),
            "verbose": self.verbose,
        }
