import pytest
from cherenkov.core.base_scanner import Severity

_mod = pytest.importorskip(
    "cherenkov.scanners.mobile.android_scanner",
    reason="AndroidScanner not yet implemented — issue #187",
)
AndroidScanner = _mod.AndroidScanner

pytestmark = pytest.mark.ai_generated


@pytest.mark.asyncio
async def test_android_scanner_findings():
    scanner = AndroidScanner()
    result = await scanner.scan("test.apk")

    assert result.scanner_name == "android"
