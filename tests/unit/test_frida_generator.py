from cherenkov.core.frida_generator import FridaGenerator

def test_frida_generator_android_ssl_pinning():
    script = FridaGenerator.generate("android", ["ssl_pinning"])
    assert "/* CHERENKOV FRIDA GENERATOR // PLATFORM: ANDROID */" in script
    assert "Android SSL Pinning Bypass" in script
    assert "TrustManagerImpl" in script

def test_frida_generator_android_root_detection():
    script = FridaGenerator.generate("android", ["root_detection"])
    assert "Android Root Detection Bypass" in script
    assert "com.noshufou.android.su" in script

def test_frida_generator_ios_ssl_pinning():
    script = FridaGenerator.generate("ios", ["ssl_pinning"])
    assert "/* CHERENKOV FRIDA GENERATOR // PLATFORM: IOS */" in script
    assert "iOS SSL Pinning Bypass" in script

def test_frida_generator_empty_hooks():
    script = FridaGenerator.generate("android", [])
    assert "/* CHERENKOV FRIDA GENERATOR // PLATFORM: ANDROID */" in script
    # Should only contain header
    lines = [l for l in script.split("\n") if l.strip()]
    assert len(lines) == 1
