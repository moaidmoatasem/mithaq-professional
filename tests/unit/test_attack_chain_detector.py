"""Unit tests for AttackChainDetector."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cherenkov.scanners.attack_chain_detector import AttackChainDetector


@pytest.mark.asyncio
async def test_returns_scan_result_structure():
    scanner = AttackChainDetector()
    with patch.object(scanner, "_http_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = Exception("timeout")
        result = await scanner.scan("http://target.example.com")

    assert result.scanner_name == "attack_chain_detector"
    assert result.target == "http://target.example.com"
    assert isinstance(result.findings, list)
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_detects_git_exposure():
    scanner = AttackChainDetector()

    async def fake_request(url, timeout):
        m = MagicMock()
        m.status_code = 200 if "/.git/HEAD" in url else 404
        return m

    with patch.object(scanner, "_http_request", side_effect=fake_request):
        result = await scanner.scan("http://target.example.com")

    assert any(".git" in f.title for f in result.findings)
    assert result.findings[0].severity.value == "CRITICAL"


@pytest.mark.asyncio
async def test_detects_console_rce_chain():
    scanner = AttackChainDetector()

    async def fake_request(url, timeout):
        m = MagicMock()
        m.status_code = 200 if url.endswith("/console") else 404
        return m

    with patch.object(scanner, "_http_request", side_effect=fake_request):
        result = await scanner.scan("http://target.example.com")

    assert any("console" in f.title for f in result.findings)


@pytest.mark.asyncio
async def test_no_findings_on_clean_target():
    scanner = AttackChainDetector()

    async def fake_request(url, timeout):
        m = MagicMock()
        m.status_code = 404
        return m

    with patch.object(scanner, "_http_request", side_effect=fake_request):
        result = await scanner.scan("http://target.example.com")

    assert result.findings == []


@pytest.mark.asyncio
async def test_multiple_chains_detected():
    scanner = AttackChainDetector()

    async def fake_request(url, timeout):
        m = MagicMock()
        m.status_code = 200 if any(p in url for p in ["/.env", "/.git/HEAD", "/console"]) else 404
        return m

    with patch.object(scanner, "_http_request", side_effect=fake_request):
        result = await scanner.scan("http://target.example.com")

    assert len(result.findings) >= 3


def test_scanner_metadata():
    s = AttackChainDetector()
    assert s.name == "attack_chain_detector"
    assert "chain" in s.description.lower()
