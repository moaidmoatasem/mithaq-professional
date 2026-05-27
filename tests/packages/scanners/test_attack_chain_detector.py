"""Unit tests for AttackChainDetectorScanner."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.attack_chain_detector_scanner import AttackChainDetectorScanner


class TestAttackChainDetectorScanner:
    """Test suite for AttackChainDetectorScanner."""

    @pytest.mark.asyncio
    async def test_detects_attack_chain_on_success(self):
        """Mock _http_request to return a 200 OK response.

        Verify scan returns a single Finding with expected title and severity.
        """
        scanner = AttackChainDetectorScanner()
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        with patch.object(
            scanner, "_http_request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_req:
            result = await scanner.scan("http://target.example.com")

            mock_req.assert_called_once_with("http://target.example.com", 10.0)
            assert len(result.findings) == 1
            finding = result.findings[0]
            assert finding.title == "Potential Attack Chain Detected"
            assert finding.severity == Severity.MEDIUM
            assert finding.cwe == "CWE-799"
            assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_handles_request_error(self):
        """Mock _http_request to raise httpx.RequestError.

        Verify scan catches exception and returns ScanResult with status="failed".
        """
        scanner = AttackChainDetectorScanner()

        with patch.object(scanner, "_http_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = httpx.RequestError("Connection failed")
            result = await scanner.scan("http://target.example.com")

            mock_req.assert_called_once_with("http://target.example.com", 10.0)
            assert len(result.findings) == 0
            assert result.status == "failed"

    def test_scanner_name(self):
        """Verify the scanner name is AttackChainDetectorScanner."""
        scanner = AttackChainDetectorScanner()
        assert scanner.name == "AttackChainDetectorScanner"
