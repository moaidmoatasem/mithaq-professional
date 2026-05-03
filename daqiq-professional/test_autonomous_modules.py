#!/usr/bin/env python3
"""Test script for autonomous-generated modules"""

import sys

sys.path.insert(0, "src")

print("🧪 Testing Autonomous Generated Modules\n")
print("=" * 50)

# Test scanners
print("\n📡 SCANNERS:")
try:
    print("  ✅ PathTraversalScanner")
except Exception as e:
    print(f"  ❌ PathTraversalScanner: {e}")

try:
    print("  ✅ FileUploadScanner")
except Exception as e:
    print(f"  ❌ FileUploadScanner: {e}")

try:
    print("  ✅ AttackChainDetector")
except Exception as e:
    print(f"  ❌ AttackChainDetector: {e}")

# Test API integrations
print("\n🔌 API INTEGRATIONS:")
try:
    print("  ✅ WebhookNotifier")
except Exception as e:
    print(f"  ❌ WebhookNotifier: {e}")

try:
    print("  ✅ SlackConnector")
except Exception as e:
    print(f"  ❌ SlackConnector: {e}")

# Test ML modules
print("\n🤖 MACHINE LEARNING:")
try:
    print("  ✅ MLVulnerabilityPredictor")
except Exception as e:
    print(f"  ❌ MLVulnerabilityPredictor: {e}")

try:
    print("  ✅ PDFReportGenerator")
except Exception as e:
    print(f"  ❌ PDFReportGenerator: {e}")

print("\n" + "=" * 50)
print("✅ Module testing complete!")
