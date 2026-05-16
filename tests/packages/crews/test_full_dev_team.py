#!/usr/bin/env python3
"""
Test the complete autonomous development team
"""

import pytest
from cherenkov.crews.autonomous_dev_team import AutonomousDevTeam


@pytest.mark.integration
def test_full_dev_team():
    # Define your project
    project_description = """
    Create a secure API gateway with:
    1. Rate limiting
    2. JWT authentication
    3. Request validation
    4. SQL injection prevention
    5. XSS protection
    6. Logging and monitoring
    """

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  🚀 AUTONOMOUS SOFTWARE DEVELOPMENT TEAM                     ║
    ║                                                              ║
    ║  Team Members:                                               ║
    ║  • Product Manager (Roadmap & Milestones)                    ║
    ║  • Technical Architect (HLD/LLD & Patterns)                  ║
    ║  • Tech Lead (Code Review & Standards)                       ║
    ║  • Senior Developer (Core Features)                          ║
    ║  • Backend Developer (APIs & Services)                       ║
    ║  • Security Developer (Security Features)                    ║
    ║  • Code Reviewer (Quality Assurance)                         ║
    ║  • QA Engineer (Testing)                                     ║
    ║  • DevOps Engineer (CI/CD & Deployment)                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Run the project
    team = AutonomousDevTeam()
    team.run_project(project_description)

    print("\n✅ Development cycle complete!")
    print("📂 Check output/autonomous_project/ for all deliverables")


if __name__ == "__main__":
    test_full_dev_team()
