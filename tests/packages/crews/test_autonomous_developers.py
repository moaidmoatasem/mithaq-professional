import os

import pytest

from cherenkov.crews.autonomous_developer_crew import AutonomousDeveloperCrew


@pytest.mark.integration
def test_autonomous_developers():
    # Create output directory
    os.makedirs("output", exist_ok=True)

    print("=" * 70)
    print("🤖 TESTING AUTONOMOUS CODE-WRITING AGENTS")
    print("=" * 70)

    # Create and run the crew
    crew = AutonomousDeveloperCrew()

    result = crew.run(vulnerability_type="SQL Injection")

    print("\n" + "=" * 70)
    print("📋 CREW EXECUTION COMPLETE")
    print("=" * 70)
    print(result)

    # Check what files were created
    print("\n📁 Generated Files:")
    if os.path.exists("output"):
        for file in os.listdir("output"):
            file_path = os.path.join("output", file)
            size = os.path.getsize(file_path)
            print(f"   ✅ {file} ({size} bytes)")


if __name__ == "__main__":
    test_autonomous_developers()
