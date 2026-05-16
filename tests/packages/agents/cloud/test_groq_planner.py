from unittest.mock import MagicMock, patch

import pytest
from cherenkov.agents.cloud.strategic_planner import StrategicPlanner, ThreatAnalysisTask
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.integration
@patch("cherenkov.agents.cloud.strategic_planner.Groq")
def test_groq_planner(mock_groq_class):
    # Test strategic planner
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mock plan"))]
    mock_response.usage = MagicMock(total_tokens=42)
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    planner = StrategicPlanner()

    task = ThreatAnalysisTask(
        target_type="mobile",
        abstract_context={
            "platform": "Android",
            "app_category": "Banking",
            "permissions_count": 15,
            "min_sdk": 21,
            "target_sdk": 34,
        },
        analysis_scope=["threat_model", "code_review", "permission_analysis"],
    )

    print("🔍 Testing Groq Strategic Planner...\n")
    result = planner.plan_security_audit(task)
    print("📋 Strategic Plan:")
    print("=" * 60)
    print(result["plan"])
    print("=" * 60)
    print(f"\n✅ Model: {result['model']}")
    print(f"📊 Tokens used: {result['tokens_used']}")


if __name__ == "__main__":
    test_groq_planner()
