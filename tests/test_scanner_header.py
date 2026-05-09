import pytest
from cherenkov.scanners.header_scanner import SimpleScanner


@pytest.mark.asyncio
async def test_scanner_returns_scan_result():
    scanner = SimpleScanner("test", "test scanner")
    result = await scanner.scan("https://example.com")
    assert result is not None
    assert result.target == "https://example.com"
    assert result.scanner_name == "test"
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_scanner_rejects_invalid_scheme():
    scanner = SimpleScanner("test", "test scanner")
    with pytest.raises(ValueError, match="Unsupported scheme"):
        await scanner.scan("ftp://example.com")


@pytest.mark.asyncio
async def test_scanner_rejects_missing_hostname():
    scanner = SimpleScanner("test", "test scanner")
    with pytest.raises(ValueError, match="Invalid URL"):
        await scanner.scan("http://")
