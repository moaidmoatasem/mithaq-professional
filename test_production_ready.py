#!/usr/bin/env python3
"""
Production Readiness Test Suite
Tests all systems before going live
"""

import subprocess
import sys
import time
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║  🧪 PRODUCTION READINESS TEST SUITE                         ║
╚══════════════════════════════════════════════════════════════╝
""")

tests_passed = 0
tests_failed = 0

def test(name, func):
    """Run a test"""
    global tests_passed, tests_failed
    print(f"\n{'='*70}")
    print(f"🧪 {name}")
    print('='*70)
    
    try:
        func()
        print(f"✅ PASSED: {name}")
        tests_passed += 1
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {name}")
        print(f"   Error: {e}")
        tests_failed += 1
        return False
    except Exception as e:
        print(f"❌ ERROR: {name}")
        print(f"   Exception: {e}")
        tests_failed += 1
        return False

# Test 1: Ollama Service
def test_ollama():
    result = subprocess.run(['ollama', 'list'], capture_output=True)
    assert result.returncode == 0, "Ollama not running"
    print("✓ Ollama service operational")

# Test 2: AI Model Loaded
def test_model():
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    assert 'qwen2.5:3b' in result.stdout or 'deepseek' in result.stdout, "No AI model loaded"
    print("✓ AI model available")

# Test 3: Scanner Modules
def test_scanners():
    scanners = list(Path('cherenkov/scanners').glob('*.py'))
    assert len(scanners) >= 3, f"Only {len(scanners)} scanners found"
    print(f"✓ {len(scanners)} scanner modules available")

# Test 4: Run Quick Scan
def test_quick_scan():
    result = subprocess.run(
        ['python', 'cherenkov_simple_scanner.py', 'https://example.com'],
        capture_output=True,
        timeout=30
    )
    assert result.returncode == 0, "Scanner failed"
    print("✓ Quick scan successful")

# Test 5: AI Agents
def test_ai_agents():
    agents = list(Path('cherenkov/agents').rglob('*.py'))
    assert len(agents) >= 5, f"Only {len(agents)} agents found"
    print(f"✓ {len(agents)} AI agents available")

# Test 6: Memory Efficiency
def test_memory():
    from cherenkov.core.memory_efficient_parallel import MemoryEfficientCrew
    crew = MemoryEfficientCrew(batch_size=2)
    assert crew.batch_size == 2, "Batch configuration failed"
    print("✓ Memory-efficient system configured")

# Test 7: Framework Structure
def test_structure():
    required = ['cherenkov/agents', 'cherenkov/core', 'cherenkov/scanners', 'cherenkov/crews']
    for path in required:
        assert Path(path).exists(), f"Missing: {path}"
    print(f"✓ All {len(required)} core directories present")

# Test 8: Dependencies
def test_dependencies():
    try:
        import crewai
        import requests
        import ollama
        print("✓ All Python dependencies installed")
    except ImportError as e:
        raise AssertionError(f"Missing dependency: {e}")

# Run all tests
print("\n🚀 Starting production readiness tests...\n")

test("Ollama Service Running", test_ollama)
test("AI Model Loaded", test_model)
test("Scanner Modules", test_scanners)
test("Quick Security Scan", test_quick_scan)
test("AI Agents Available", test_ai_agents)
test("Memory Efficiency", test_memory)
test("Framework Structure", test_structure)
test("Python Dependencies", test_dependencies)

# Summary
print("\n" + "="*70)
print("📊 PRODUCTION READINESS SUMMARY")
print("="*70)
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print(f"📈 Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")

if tests_failed == 0:
    print("\n🎉 SYSTEM IS PRODUCTION READY!")
    print("✅ All critical systems operational")
    print("✅ Ready for real-world security testing")
    sys.exit(0)
else:
    print(f"\n⚠️  {tests_failed} test(s) failed")
    print("Fix issues before production deployment")
    sys.exit(1)

