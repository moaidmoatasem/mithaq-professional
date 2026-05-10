import sys
from pathlib import Path

import pytest
from flask import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from cherenkov_web import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_run_scan_invalid_url_format(client):
    # This URL should trigger an exception in urlparse, specifically a ValueError
    # for invalid IPv6 URL in modern python versions.
    # It tests the "except Exception:" block at the end of the try block in run_scan().
    response = client.post("/api/scan", json={"url": "http://[::1"})

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Invalid URL format"


def test_run_scan_missing_body(client):
    response = client.post("/api/scan", json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["error"] == "Request body is required"


def test_run_scan_missing_url(client):
    response = client.post("/api/scan", json={"other": "value"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["error"] == "URL is required"


def test_run_scan_invalid_scheme(client):
    response = client.post("/api/scan", json={"url": "ftp://example.com"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["error"] == "Only http/https URLs are supported"


def test_run_scan_missing_hostname(client):
    response = client.post("/api/scan", json={"url": "http://"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["error"] == "Invalid URL: missing hostname"
