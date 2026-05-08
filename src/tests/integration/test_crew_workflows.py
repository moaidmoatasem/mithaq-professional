"""Integration tests for SecurityCrew workflows."""

from unittest.mock import Mock, patch

from cherenkov.agents.architect_agent import ArchitectAgent
from cherenkov.agents.developer_agent import DeveloperAgent
from cherenkov.agents.tester_agent import TesterAgent
from cherenkov.crews.security_crew import SecurityCrew


class TestCrewWorkflows:
    """Test end-to-end crew workflows."""

    @patch("cherenkov.crews.security_crew.Crew")
    def test_full_security_audit_workflow(self, mock_crew_class):
        """Test complete security audit with all agents."""
        # Mock crew execution
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Complete security audit results"
        mock_crew_class.return_value = mock_crew_instance

        # Create crew
        crew = SecurityCrew()

        # Execute full audit
        result = crew.perform_security_audit(
            target="mobile-banking-app",
            scope=["threat_model", "code_review", "pentest"],
        )

        # Verify all agents involved
        assert result["agents_used"] == 3
        assert result["target"] == "mobile-banking-app"
        assert "threat_model" in result["scope"]
        assert "code_review" in result["scope"]
        assert "pentest" in result["scope"]

    @patch("cherenkov.crews.security_crew.Crew")
    def test_mobile_app_analysis_workflow(self, mock_crew_class):
        """Test mobile app analysis end-to-end."""
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Mobile app analysis complete"
        mock_crew_class.return_value = mock_crew_instance

        crew = SecurityCrew()

        result = crew.analyze_mobile_app(apk_path="/home/user/banking.apk")

        assert result["apk_path"] == "/home/user/banking.apk"
        assert result["analysis_type"] == "mobile_security"
        assert result["agents_used"] == 3

    def test_architect_developer_integration(self):
        """Test Architect → Developer workflow."""
        architect = ArchitectAgent()
        developer = DeveloperAgent()

        # Verify agents are compatible
        assert architect.config.role == "Security Architect"
        assert developer.config.role == "Security Developer"

        # Verify both have agent instances
        assert architect.agent is not None
        assert developer.agent is not None

    def test_developer_tester_integration(self):
        """Test Developer → Tester workflow."""
        developer = DeveloperAgent()
        tester = TesterAgent()

        # Verify agents are compatible
        assert developer.config.role == "Security Developer"
        assert tester.config.role == "Security Tester"

        # Verify both have agent instances
        assert developer.agent is not None
        assert tester.agent is not None

    def test_all_agents_capabilities(self):
        """Test that all agents have required capabilities."""
        architect = ArchitectAgent()
        developer = DeveloperAgent()
        tester = TesterAgent()

        # Verify agent capabilities
        arch_caps = architect.get_capabilities()
        dev_caps = developer.get_capabilities()
        test_caps = tester.get_capabilities()

        # Check capabilities structure
        assert arch_caps["role"] == "Security Architect"
        assert "threat modeling" in arch_caps["goal"].lower()

        assert dev_caps["role"] == "Security Developer"
        assert "code" in dev_caps["goal"].lower()

        assert test_caps["role"] == "Security Tester"
        assert "penetration" in test_caps["goal"].lower() or "testing" in test_caps["goal"].lower()

    @patch("cherenkov.crews.security_crew.Crew")
    def test_crew_with_custom_agents(self, mock_crew_class):
        """Test crew with custom agent configurations."""
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Custom audit complete"
        mock_crew_class.return_value = mock_crew_instance

        # Create custom agents
        architect = ArchitectAgent()
        developer = DeveloperAgent()
        tester = TesterAgent()

        # Create crew with custom agents
        crew = SecurityCrew(
            architect=architect,
            developer=developer,
            tester=tester,
            verbose=False,
        )

        result = crew.perform_security_audit(
            target="custom-target",
            scope=["threat_model"],
        )

        assert result["target"] == "custom-target"
        assert crew.verbose is False

    def test_crew_info_integration(self):
        """Test crew information reflects all agents."""
        crew = SecurityCrew()
        info = crew.get_crew_info()

        assert len(info["agents"]) == 3
        assert info["agents"]["architect"] == "Security Architect"
        assert info["agents"]["developer"] == "Security Developer"
        assert info["agents"]["tester"] == "Security Tester"

    def test_all_agents_have_crewai_agents(self):
        """Test all agents have CrewAI agent instances."""
        architect = ArchitectAgent()
        developer = DeveloperAgent()
        tester = TesterAgent()

        assert architect.agent is not None
        assert developer.agent is not None
        assert tester.agent is not None

    def test_crew_sequential_execution_order(self):
        """Test crew maintains sequential execution order."""
        from crewai import Process

        crew = SecurityCrew(process=Process.sequential)

        assert crew.process == Process.sequential
        assert crew.architect is not None
        assert crew.developer is not None
        assert crew.tester is not None

    def test_crew_hierarchical_execution_support(self):
        """Test crew supports hierarchical execution."""
        from crewai import Process

        crew = SecurityCrew(process=Process.hierarchical)

        assert crew.process == Process.hierarchical
        assert len(crew.get_crew_info()["agents"]) == 3
