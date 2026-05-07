from mithaq.agents.cloud.strategic_planner import StrategicPlanner, ThreatAnalysisTask
from dotenv import load_dotenv

load_dotenv()

# Test strategic planner
planner = StrategicPlanner()

task = ThreatAnalysisTask(
    target_type="mobile",
    abstract_context={
        "platform": "Android",
        "app_category": "Banking",
        "permissions_count": 15,
        "min_sdk": 21,
        "target_sdk": 34
    },
    analysis_scope=["threat_model", "code_review", "permission_analysis"]
)

print("🔍 Testing Groq Strategic Planner...\n")
result = planner.plan_security_audit(task)
print("📋 Strategic Plan:")
print("=" * 60)
print(result["plan"])
print("=" * 60)
print(f"\n✅ Model: {result['model']}")
print(f"📊 Tokens used: {result['tokens_used']}")

