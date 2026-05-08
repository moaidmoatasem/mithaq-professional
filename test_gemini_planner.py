from cherenkov.agents.cloud.strategic_planner import StrategicPlanner, ThreatAnalysisTask
from dotenv import load_dotenv
import os

load_dotenv()

# Check if Gemini API key is present
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️ GOOGLE_API_KEY not found. Skipping Gemini test.")
    exit(0)

# Test strategic planner with Gemini
print("🔍 Testing Gemini Strategic Planner...\n")
planner = StrategicPlanner(provider="gemini", model="gemini-1.5-flash")

task = ThreatAnalysisTask(
    target_type="web",
    abstract_context={
        "framework": "React",
        "backend": "Node.js",
        "auth": "OAuth2",
        "database": "PostgreSQL",
    },
    analysis_scope=["recon", "vulnerability_scanning", "exploit_dev"]
)

try:
    result = planner.plan_security_audit(task)
    print("📋 Strategic Plan:")
    print("=" * 60)
    print(result["plan"])
    print("=" * 60)
    print(f"\n✅ Model: {result['model']}")
    print(f"📊 Tokens used: {result['tokens_used']}")
except Exception as e:
    print(f"❌ Gemini Test Failed: {e}")
