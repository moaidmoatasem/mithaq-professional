import pytest
from unittest.mock import MagicMock, patch
import httpx

from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.cicd_integration_scanner import CICDIntegrationScanner


@pytest.mark.asyncio
async def test_cicd_scanner_git_exposure():
    scanner = CICDIntegrationScanner()
    target = "http://vulnerable.local"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "[core]\nrepositoryformatversion=0"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            if "/.git/config" in url:
                return mock_response
            # Return a non-matching 404 response for other paths
            res_404 = MagicMock(spec=httpx.Response)
            res_404.status_code = 404
            res_404.text = "Not Found"
            return res_404

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert result.target == target
    assert result.scanner_name == "cicd_integration_scanner"
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.severity == Severity.HIGH
    assert finding.cwe == "CWE-538"
    assert "Git Configuration" in finding.title
    assert "Exposing the Git directory" in finding.description


@pytest.mark.asyncio
async def test_cicd_scanner_github_workflow_exposure():
    scanner = CICDIntegrationScanner()
    target = "http://workflow.local"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "name: CI Workflow\njobs:\n  build:\n    runs-on: ubuntu-latest"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            if "/.github/workflows/ci.yml" in url:
                return mock_response
            res_404 = MagicMock(spec=httpx.Response)
            res_404.status_code = 404
            res_404.text = "Not Found"
            return res_404

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.severity == Severity.MEDIUM
    assert finding.cwe == "CWE-538"
    assert "GitHub Actions Workflow" in finding.title


@pytest.mark.asyncio
async def test_cicd_scanner_jenkins_api_exposure():
    scanner = CICDIntegrationScanner()
    target = "http://jenkins.local"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = '{"_class":"jenkins.model.Jenkins","jobs":[],"primaryView":{}}'

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            if "/api/json" in url:
                return mock_response
            res_404 = MagicMock(spec=httpx.Response)
            res_404.status_code = 404
            res_404.text = "Not Found"
            return res_404

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.severity == Severity.HIGH
    assert finding.cwe == "CWE-200"
    assert "Jenkins Build Engine API" in finding.title


@pytest.mark.asyncio
async def test_cicd_scanner_safe_endpoint():
    scanner = CICDIntegrationScanner()
    target = "http://safe.local"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "<html><body>Welcome to our corporate homepage!</body></html>"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert len(result.findings) == 0
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_cicd_scanner_network_timeout():
    scanner = CICDIntegrationScanner()
    target = "http://timeout.local"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            raise httpx.TimeoutException("Connection timed out")

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert len(result.findings) == 0
    assert result.status == "completed"
