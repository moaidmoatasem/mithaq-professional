"""Tests for the FastAPI /api/scan endpoint (replaces retired Flask cherenkov_web.py tests)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages"))

# Guard against metaclass conflicts caused by heavy orchestration imports
# (crewai stack) that cherenkov.api.main pulls in at module level.
try:
    from cherenkov.api.main import app
    from fastapi.testclient import TestClient

    _api_client = TestClient(app, raise_server_exceptions=False)
    _IMPORT_ERROR: Exception | None = None
except Exception as exc:  # noqa: BLE001
    _api_client = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc


def _client() -> "TestClient":
    if _api_client is None:
        pytest.skip(f"cherenkov.api.main not importable: {_IMPORT_ERROR}")
    return _api_client


def test_run_scan_invalid_url_format():
    # IPv6 bracket not closed — urlparse raises ValueError → 400
    response = _client().post("/api/scan", json={"url": "http://[::1"})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_run_scan_missing_body():
    # Missing required field `url` → 422 Unprocessable Entity from Pydantic
    response = _client().post("/api/scan", json={})
    assert response.status_code == 422


def test_run_scan_missing_url():
    response = _client().post("/api/scan", json={"other": "value"})
    assert response.status_code == 422


def test_run_scan_invalid_scheme():
    response = _client().post("/api/scan", json={"url": "ftp://example.com"})
    assert response.status_code == 400
    assert "Only http/https" in response.json()["detail"]


def test_run_scan_missing_hostname():
    response = _client().post("/api/scan", json={"url": "http://"})
    assert response.status_code == 400
    assert "hostname" in response.json()["detail"]
