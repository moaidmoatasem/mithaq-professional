from cherenkov.core.hybrid_orchestrator import ExecutionMode, HybridOrchestrator
from dotenv import load_dotenv

load_dotenv()

# Simulate sensitive local context
local_context = {
    "app_name": "MobileBankingApp",
    "api_key": "sk_live_abcdef1234567890",
    "database_url": "postgresql://admin:secret@localhost:5432/banking",
    "permissions": ["CAMERA", "LOCATION", "CONTACTS", "SMS"],
    "min_sdk": 21,
    "target_sdk": 34,
    "package_name": "com.example.banking",
}

print("=" * 70)
print("🧪 TESTING HYBRID CLOUD-LOCAL ORCHESTRATOR")
print("=" * 70)

# Create orchestrator
orchestrator = HybridOrchestrator()

# Execute hybrid audit
result = orchestrator.execute_security_audit(
    target_type="mobile",
    local_context=local_context,
    analysis_scope=["threat_model", "permission_analysis", "code_review"],
    mode=ExecutionMode.HYBRID,
)

print("\n" + "=" * 70)
print("📋 FINAL AUDIT RESULT")
print("=" * 70)
print(f"Success: {result['success']}")
print(f"Task: {result['task_name']}")
print(f"Execution Mode: {result['execution_mode']}")
print(f"Tokens Used: {result['tokens_used']}")
print("\nRedaction Summary:")
print(f"  - Redacted Fields: {', '.join(result['redacted_fields'])}")
print(f"  - Hash: {result['output']['redaction_summary']['hash_signature']}")
print(f"  - Safe for Cloud: {result['output']['redaction_summary']['is_safe']}")

print("\n" + "=" * 70)
print("📊 EXECUTION SUMMARY")
print("=" * 70)
summary = orchestrator.get_execution_summary()
for key, value in summary.items():
    print(f"{key}: {value}")
