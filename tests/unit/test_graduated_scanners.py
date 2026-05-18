"""Unit tests for the three graduated scanners: CSRF, XSS, OpenRedirect.

All HTTP calls are mocked — no network required.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.refined.csrf_scanner import CSRFScanner
from cherenkov.scanners.refined.open_redirect_scanner import OpenRedirectScanner
from cherenkov.scanners.refined.xss_scanner import XSSScanner

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_http_response(
    status_code: int = 200,
    text: str = "",
    headers: dict | None = None,
) -> AsyncMock:
    """Build an AsyncMock that looks like an httpx.Response."""
    resp = AsyncMock()
    resp.status_code = status_code
    resp.text = text
    resp.headers = headers or {}
    return resp


def _make_async_client_mock(get_response: AsyncMock) -> MagicMock:
    """Wrap a response in a context-manager-compatible AsyncClient mock."""
    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.get = AsyncMock(return_value=get_response)
    return client


# ---------------------------------------------------------------------------
# CSRFScanner
# ---------------------------------------------------------------------------

class TestCSRFScanner:
    def setup_method(self):
        self.scanner = CSRFScanner()

    @pytest.mark.asyncio
    async def test_detects_form_without_csrf_token(self):
        html = '<html><body><form method="post"><input type="text"></form></body></html>'
        resp = _mock_http_response(text=html, headers={})

        with patch.object(self.scanner, "_http_request", AsyncMock(return_value=resp)):
            result = await self.scanner.scan("http://localhost/login")

        assert result.target == "http://localhost/login"
        titles = [f.title for f in result.findings]
        assert "Missing CSRF Token" in titles
        csrf_finding = next(f for f in result.findings if f.title == "Missing CSRF Token")
        assert csrf_finding.severity == Severity.HIGH
        assert csrf_finding.cwe == "CWE-352"

    @pytest.mark.asyncio
    async def test_no_finding_when_csrf_token_present(self):
        html = '<form><input name="csrf_token" value="abc123"></form>'
        resp = _mock_http_response(text=html, headers={})

        with patch.object(self.scanner, "_http_request", AsyncMock(return_value=resp)):
            result = await self.scanner.scan("http://localhost/login")

        csrf_findings = [f for f in result.findings if f.title == "Missing CSRF Token"]
        assert len(csrf_findings) == 0

    @pytest.mark.asyncio
    async def test_detects_missing_samesite_cookie(self):
        resp = _mock_http_response(
            text="",
            headers={"set-cookie": "session=abc; Path=/; HttpOnly"},
        )

        with patch.object(self.scanner, "_http_request", AsyncMock(return_value=resp)):
            result = await self.scanner.scan("http://localhost/")

        titles = [f.title for f in result.findings]
        assert "Missing SameSite Cookie Attribute" in titles
        finding = next(f for f in result.findings if "SameSite" in f.title)
        assert finding.severity == Severity.MEDIUM

    @pytest.mark.asyncio
    async def test_no_finding_when_samesite_present(self):
        resp = _mock_http_response(
            text="",
            headers={"set-cookie": "session=abc; Path=/; SameSite=Lax"},
        )

        with patch.object(self.scanner, "_http_request", AsyncMock(return_value=resp)):
            result = await self.scanner.scan("http://localhost/")

        samesite_findings = [f for f in result.findings if "SameSite" in f.title]
        assert len(samesite_findings) == 0

    @pytest.mark.asyncio
    async def test_no_findings_on_page_without_forms(self):
        resp = _mock_http_response(text="<html><body><p>Hello</p></body></html>", headers={})

        with patch.object(self.scanner, "_http_request", AsyncMock(return_value=resp)):
            result = await self.scanner.scan("http://localhost/")

        csrf_findings = [f for f in result.findings if f.title == "Missing CSRF Token"]
        assert len(csrf_findings) == 0

    @pytest.mark.asyncio
    async def test_handles_network_error_gracefully(self):
        with patch.object(
            self.scanner,
            "_http_request",
            AsyncMock(side_effect=httpx.TimeoutException("timeout")),
        ):
            result = await self.scanner.scan("http://localhost/")

        assert result.status == "completed"
        assert len(result.findings) == 0

    def test_scanner_name(self):
        assert self.scanner.name == "csrf"

    def test_scanner_registered_key(self):
        """Registry derives key as class_name.replace('Scanner','').lower()."""
        assert CSRFScanner.__name__.replace("Scanner", "").lower() == "csrf"


# ---------------------------------------------------------------------------
# XSSScanner
# ---------------------------------------------------------------------------

class TestXSSScanner:
    def setup_method(self):
        self.scanner = XSSScanner()

    @pytest.mark.asyncio
    async def test_detects_reflected_xss(self):
        payload = '<script>alert("XSS")</script>'
        reflected_resp = _mock_http_response(text=payload)
        clean_resp = _mock_http_response(text="<html></html>")

        mock_client = _make_async_client_mock(reflected_resp)
        # First call (param injection) reflects payload; second call (DOM check) is clean.
        mock_client.get = AsyncMock(side_effect=[reflected_resp, clean_resp])

        with patch(
            "cherenkov.scanners.refined.xss_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/?q=test")

        xss_findings = [f for f in result.findings if f.title == "Reflected XSS"]
        assert len(xss_findings) >= 1
        assert xss_findings[0].severity == Severity.HIGH
        assert xss_findings[0].cwe == "CWE-79"

    @pytest.mark.asyncio
    async def test_no_xss_when_payload_not_reflected(self):
        safe_resp = _mock_http_response(text="<html>safe</html>")
        mock_client = _make_async_client_mock(safe_resp)

        with patch(
            "cherenkov.scanners.refined.xss_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/?q=test")

        xss_findings = [f for f in result.findings if f.title == "Reflected XSS"]
        assert len(xss_findings) == 0

    @pytest.mark.asyncio
    async def test_detects_dom_xss_sink(self):
        dom_resp = _mock_http_response(text="var x = document.write(userInput);")
        mock_client = _make_async_client_mock(dom_resp)

        with patch(
            "cherenkov.scanners.refined.xss_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/")

        dom_findings = [f for f in result.findings if "DOM XSS" in f.title]
        assert len(dom_findings) >= 1
        assert dom_findings[0].severity == Severity.MEDIUM

    @pytest.mark.asyncio
    async def test_skips_target_without_params(self):
        """No reflected XSS checks run if the URL has no query parameters."""
        safe_resp = _mock_http_response(text="<html></html>")
        mock_client = _make_async_client_mock(safe_resp)

        with patch(
            "cherenkov.scanners.refined.xss_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/")

        reflected = [f for f in result.findings if f.title == "Reflected XSS"]
        assert len(reflected) == 0

    @pytest.mark.asyncio
    async def test_handles_request_error_gracefully(self):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(
            side_effect=httpx.RequestError("connection refused")
        )
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "cherenkov.scanners.refined.xss_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/?q=test")

        assert result.status == "completed"

    def test_scanner_name(self):
        assert self.scanner.name == "xss"


# ---------------------------------------------------------------------------
# OpenRedirectScanner
# ---------------------------------------------------------------------------

class TestOpenRedirectScanner:
    def setup_method(self):
        self.scanner = OpenRedirectScanner()

    @pytest.mark.asyncio
    async def test_detects_open_redirect(self):
        redirect_resp = _mock_http_response(
            status_code=302,
            headers={"location": "http://evil.com/phish"},
        )
        mock_client = _make_async_client_mock(redirect_resp)

        with patch(
            "cherenkov.scanners.refined.open_redirect_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/?redirect=http://legitimate.com")

        or_findings = [f for f in result.findings if f.title == "Open Redirect"]
        assert len(or_findings) >= 1
        assert or_findings[0].severity == Severity.MEDIUM
        assert or_findings[0].cwe == "CWE-601"

    @pytest.mark.asyncio
    async def test_no_finding_when_redirect_is_safe(self):
        safe_resp = _mock_http_response(
            status_code=302,
            headers={"location": "http://localhost/dashboard"},
        )
        mock_client = _make_async_client_mock(safe_resp)

        with patch(
            "cherenkov.scanners.refined.open_redirect_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/?redirect=http://legitimate.com")

        or_findings = [f for f in result.findings if f.title == "Open Redirect"]
        assert len(or_findings) == 0

    @pytest.mark.asyncio
    async def test_no_check_when_no_redirect_params(self):
        """Scanner should not make any requests if no redirect params are in the URL."""
        result = await self.scanner.scan("http://localhost/search?q=hello")
        assert len(result.findings) == 0

    @pytest.mark.asyncio
    async def test_handles_timeout_gracefully(self):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        with patch(
            "cherenkov.scanners.refined.open_redirect_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/?next=http://example.com")

        assert result.status == "completed"
        assert len(result.findings) == 0

    @pytest.mark.asyncio
    async def test_non_redirect_status_code_not_flagged(self):
        ok_resp = _mock_http_response(status_code=200)
        mock_client = _make_async_client_mock(ok_resp)

        with patch(
            "cherenkov.scanners.refined.open_redirect_scanner.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await self.scanner.scan("http://localhost/?url=http://example.com")

        assert len(result.findings) == 0

    def test_scanner_name(self):
        assert self.scanner.name == "open_redirect"

    def test_scanner_registered_key(self):
        # Registry derives key via .replace("Scanner","").lower() → "openredirect"
        assert OpenRedirectScanner.__name__.replace("Scanner", "").lower() == "openredirect"
