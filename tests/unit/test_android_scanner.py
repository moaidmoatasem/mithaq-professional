import pytest
from cherenkov.scanners.mobile.android_scanner import AndroidScanner
from cherenkov.core.base_scanner import Severity

@pytest.mark.asyncio
async def test_android_scanner_findings():
    scanner = AndroidScanner()
    result = await scanner.scan("test.apk")
    
    assert result.scanner_name == "android"
    assert len(result.findings) == 2
    
    debug_finding = next(f for f in result.findings if "Debug Mode" in f.title)
    assert debug_finding.severity == Severity.HIGH
    assert debug_finding.cwe == "CWE-489"
    
    permission_finding = next(f for f in result.findings if "Permissions" in f.title)
    assert permission_finding.severity == Severity.LOW
    assert permission_finding.cwe == "CWE-276"
