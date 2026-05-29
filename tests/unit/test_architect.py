import pytest
from cherenkov.agents.architect import SecurityArchitect


@pytest.mark.asyncio
async def test_generate_plan_fallback():
    architect = SecurityArchitect(proxy_url="http://invalid:1234")
    result = await architect.generate_plan({"target": "test", "framework": "OWASP"})
    assert result["status"] == "success"
    assert "threat_surface" in result["plan"]
    assert result["plan"]["risk_score"] == 50
    assert "Fallback triggered due to error" in result["plan"]["reasoning"]
