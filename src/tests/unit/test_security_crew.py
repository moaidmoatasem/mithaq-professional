"""Unit tests for SecurityCrew."""

from unittest.mock import Mock, patch

from crewai import Process

from mithaq.agents.architect_agent import ArchitectAgent
from mithaq.agents.developer_agent import DeveloperAgent
from mithaq.agents.tester_agent import TesterAgent
from mithaq.crews.security_crew import SecurityCrew


class TestSecurityCrew:
    """Test suite for SecurityCrew."""

    def test_default_initialization(self):
        """Test crew initialization with default agents."""
        crew = SecurityCrew()

        assert crew.architect is not None
        assert crew.developer is not None
        assert crew.tester is not None
        assert crew.process == Process.sequential
        assert crew.verbose is True

    def test_custom_initialization(self):
        """Test crew with custom agents."""
        architect = ArchitectAgent()
        developer = DeveloperAgent()
        tester = TesterAgent()

        crew = SecurityCrew(
            architect=architect,
            developer=developer,
            tester=tester,
            process=Process.hierarchical,
            verbose=False,
        )

        assert crew.architect == architect
        assert crew.developer == developer
        assert crew.tester == tester
        assert crew.process == Process.hierarchical
        assert crew.verbose is False

    def test_get_crew_info(self):
        """Test crew information retrieval."""
        crew = SecurityCrew()

        info = crew.get_crew_info()

        assert "agents" in info
        assert info["agents"]["architect"] == "Security Architect"
        assert info["agents"]["developer"] == "Security Developer"
        assert info["agents"]["tester"] == "Security Tester"
        assert "sequential" in info["process"].lower()

    def test_create_crew_with_tasks(self):
        """Test crew creation with tasks."""
        from crewai import Task

        crew_manager = SecurityCrew()

        tasks = [
            Task(
                description="Test task 1",
                expected_output="Output 1",
                agent=crew_manager.architect.agent,
            ),
            Task(
                description="Test task 2",
                expected_output="Output 2",
                agent=crew_manager.developer.agent,
            ),
        ]

        crew = crew_manager.create_crew(tasks)

        assert crew is not None
        assert len(crew.agents) == 3  # All three agents
        assert len(crew.tasks) == 2

    @patch("mithaq.crews.security_crew.Crew")
    def test_perform_security_audit_threat_model(self, mock_crew_class):
        """Test security audit with threat modeling scope."""
        # Mock crew instance and kickoff result
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Threat model results"
        mock_crew_class.return_value = mock_crew_instance

        crew = SecurityCrew()

        result = crew.perform_security_audit(
            target="mobile-banking-app",
            scope=["threat_model"],
        )

        assert result["target"] == "mobile-banking-app"
        assert result["scope"] == ["threat_model"]
        assert result["agents_used"] == 1
        mock_crew_instance.kickoff.assert_called_once()

    @patch("mithaq.crews.security_crew.Crew")
    def test_perform_security_audit_full_scope(self, mock_crew_class):
        """Test security audit with full scope."""
        # Mock crew instance and kickoff result
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Full audit results"
        mock_crew_class.return_value = mock_crew_instance

        crew = SecurityCrew()

        result = crew.perform_security_audit(
            target="web-application",
            scope=["threat_model", "code_review", "pentest"],
        )

        assert result["target"] == "web-application"
        assert len(result["scope"]) == 3
        assert result["agents_used"] == 3
        mock_crew_instance.kickoff.assert_called_once()

    @patch("mithaq.crews.security_crew.Crew")
    def test_analyze_mobile_app(self, mock_crew_class):
        """Test mobile app analysis workflow."""
        # Mock crew instance and kickoff result
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Mobile analysis results"
        mock_crew_class.return_value = mock_crew_instance

        crew = SecurityCrew()

        result = crew.analyze_mobile_app(apk_path="/path/to/app.apk")

        assert result["apk_path"] == "/path/to/app.apk"
        assert result["analysis_type"] == "mobile_security"
        assert result["agents_used"] == 3
        mock_crew_instance.kickoff.assert_called_once()

    def test_sequential_process(self):
        """Test crew uses sequential process by default."""
        crew = SecurityCrew()

        assert crew.process == Process.sequential

    def test_hierarchical_process(self):
        """Test crew can use hierarchical process."""
        crew = SecurityCrew(process=Process.hierarchical)

        assert crew.process == Process.hierarchical

