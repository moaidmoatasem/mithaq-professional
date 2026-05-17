import pytest
from cherenkov.core.frida_generator import FridaHookGenerator

def test_frida_generator_supported_cwes():
    cwes = FridaHookGenerator.list_supported_cwes()
    assert "CWE-532" in cwes
    assert "CWE-922" in cwes
    assert "CWE-749" in cwes
    assert len(cwes) >= 3

def test_frida_generator_output_contains_cwe():
    hook = FridaHookGenerator.generate("CWE-532")
    assert "CWE-532" in hook
    assert "android.util.Log" in hook
    assert "Java.perform" in hook

def test_frida_generator_unknown_cwe():
    hook = FridaHookGenerator.generate("CWE-999")
    assert "Monitoring CWE-999" in hook
    assert "console.log" in hook

def test_frida_generator_sensitive_storage():
    hook = FridaHookGenerator.generate("CWE-922")
    assert "SharedPreferences" in hook
    assert "putString" in hook
