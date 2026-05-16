"""Unit tests for iOS scanner — IPA, binary flags, ATS"""

import json
import tempfile
from pathlib import Path

import pytest
from cherenkov.scanners.mobile.ats_scanner import AtsScanner
from cherenkov.scanners.mobile.binary_scanner import IosBinaryScanner
from cherenkov.scanners.mobile.ipa_scanner import IpaScanner


@pytest.mark.asyncio
async def test_ipa_scanner_no_plist():
    scanner = IpaScanner()
    result = await scanner.scan("/nonexistent/file.ipa")
    assert result.scanner_name == "ipa"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_ipa_scanner_arbitrary_loads():
    scanner = IpaScanner()
    result = await scanner.scan("nonexistent_file.ipa")
    assert result.scanner_name == "ipa"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_binary_scanner_not_found():
    scanner = IosBinaryScanner()
    result = await scanner.scan("/nonexistent/binary")
    assert result.scanner_name == "ios_binary"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_binary_scanner_name_hint():
    scanner = IosBinaryScanner()
    result = await scanner.scan("nopie_noarc_nostack.ipa")
    assert result.scanner_name == "ios_binary"
    findings = {f.title for f in result.findings}
    assert "Position Independent Executable (PIE) Disabled" in findings
    assert "Automatic Reference Counting (ARC) Disabled" in findings
    assert "Stack Canary Not Detected" in findings


@pytest.mark.asyncio
async def test_ats_scanner_arbitrary_loads():
    scanner = AtsScanner()
    config = {"NSAllowsArbitraryLoads": True}
    result = await scanner.scan(json.dumps(config))
    assert result.scanner_name == "ats"
    assert any("ATS Disabled" in f.title for f in result.findings)


@pytest.mark.asyncio
async def test_ats_scanner_secure_config():
    scanner = AtsScanner()
    config = {
        "NSAllowsArbitraryLoads": False,
        "NSAllowsLocalNetworking": True,
    }
    result = await scanner.scan(json.dumps(config))
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_ats_scanner_weak_tls():
    scanner = AtsScanner()
    config = {
        "NSAllowsArbitraryLoads": False,
        "NSExceptionDomains": {
            "api.example.com": {
                "NSExceptionMinimumTLSVersion": "TLSv1.0",
                "NSTemporaryExceptionAllowsInsecureHTTPLoads": True,
            }
        },
    }
    result = await scanner.scan(json.dumps(config))
    findings = {f.title for f in result.findings}
    assert "Weak TLS Version for api.example.com" in findings
    assert "ATS Exception — HTTP Allowed for api.example.com" in findings


@pytest.mark.asyncio
async def test_binary_scanner_secure_flags():
    scanner = IosBinaryScanner()
    result = await scanner.scan("secure_app.ipa")
    assert result.scanner_name == "ios_binary"
    assert len(result.findings) == 0
