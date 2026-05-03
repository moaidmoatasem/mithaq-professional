#!/usr/bin/env python3
"""Test script for autonomous-generated modules"""

import sys
sys.path.insert(0, 'src')

print("🧪 Testing Autonomous Generated Modules\n")
print("=" * 50)

# Test scanners
print("\n📡 SCANNERS:")
try:
    from daqiq.autonomous_generated.scanners.pathtraversalscanner import PathTraversalScanner
    print("  ✅ PathTraversalScanner")
except Exception as e:
    print(f"  ❌ PathTraversalScanner: {e}")

try:
    from daqiq.autonomous_generated.scanners.fileuploadscanner import FileUploadScanner
    print("  ✅ FileUploadScanner")
except Exception as e:
    print(f"  ❌ FileUploadScanner: {e}")

try:
    from daqiq.autonomous_generated.scanners.attackchaindetector import AttackChainDetector
    print("  ✅ AttackChainDetector")
except Exception as e:
    print(f"  ❌ AttackChainDetector: {e}")

# Test API integrations
print("\n🔌 API INTEGRATIONS:")
try:
    from daqiq.autonomous_generated.api.webhooknotifier import WebhookNotifier
    print("  ✅ WebhookNotifier")
except Exception as e:
    print(f"  ❌ WebhookNotifier: {e}")

try:
    from daqiq.autonomous_generated.api.slackconnector import SlackConnector
    print("  ✅ SlackConnector")
except Exception as e:
    print(f"  ❌ SlackConnector: {e}")

# Test ML modules
print("\n🤖 MACHINE LEARNING:")
try:
    from daqiq.autonomous_generated.ml.mlvulnerabilitypredictor import MLVulnerabilityPredictor
    print("  ✅ MLVulnerabilityPredictor")
except Exception as e:
    print(f"  ❌ MLVulnerabilityPredictor: {e}")

try:
    from daqiq.autonomous_generated.ml.pdfreportgenerator import PDFReportGenerator
    print("  ✅ PDFReportGenerator")
except Exception as e:
    print(f"  ❌ PDFReportGenerator: {e}")

print("\n" + "=" * 50)
print("✅ Module testing complete!")
