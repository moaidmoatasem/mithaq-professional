import json
import os
import uuid

import cherenkov
import cherenkov.core.storage.database as db
import pytest
from cherenkov.api.main import app
from cherenkov.api.middleware.auth import create_access_token, hash_password
from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def bypass_rate_limit():
    app.state.limiter.enabled = False
    yield
    app.state.limiter.enabled = True


@pytest.fixture(autouse=True)
def set_env(monkeypatch, tmp_path):
    monkeypatch.setenv("CHERENKOV_ADMIN_PASSWORD", "testpass")
    monkeypatch.setenv("CHERENKOV_JWT_SECRET", "super_secret_test_key_1234567890")
    env_file = tmp_path / ".env"
    env_file.write_text("CHERENKOV_JWT_SECRET=super_secret_test_key_1234567890\n")
    monkeypatch.setenv("ROTATION_ENV_PATH", str(env_file))


@pytest.fixture(autouse=True)
def isolate_db(tmp_path):
    test_db = tmp_path / "test_e2e_api.db"
    # patch both db_path in the module and globally
    db._DB_PATH = test_db
    db.init_db(test_db)
    db.save_user("admin", hash_password("testpass"), 3, path=test_db)
    yield test_db


@pytest.fixture
def client(isolate_db, monkeypatch):
    monkeypatch.setattr(cherenkov.core.storage.database, "_DB_PATH", isolate_db)

    # We must patch get_scan in main to use our test db path, because default args are bound early
    original_get_scan = db.get_scan

    def mock_get_scan(scan_id, path=isolate_db):
        return original_get_scan(scan_id, path=isolate_db)

    monkeypatch.setattr("cherenkov.api.main.get_scan", mock_get_scan, raising=False)

    # but wait, it imports get_scan locally in the function `v1_compliance_pdf`.
    # Let's instead patch `db._connect`
    original_connect = db._connect

    def mock_connect(path=isolate_db):
        return original_connect(path=isolate_db)

    monkeypatch.setattr(db, "_connect", mock_connect)

    with TestClient(app) as test_client:
        yield test_client


def test_e2e_pdf_generation(client, isolate_db, tmp_path):
    auth_data = {"username": "admin", "password": "testpass"}
    response = client.post("/api/v1/auth/token", json=auth_data)
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # create scan
    findings = [
        {
            "title": "Test Vuln",
            "severity": "HIGH",
            "description": "Test",
            "cwe": "79",
            "remediation": "Fix",
        }
    ]
    scan_id = str(uuid.uuid4())
    db.save_scan(
        scan_id=scan_id,
        target="http://localhost",
        findings=findings,
        status="completed",
        path=isolate_db,
    )
    db.save_scan_trace(scan_id, "test_trace_hash", {"findings": findings}, path=isolate_db)

    response = client.get(f"/api/v1/scan/{scan_id}/compliance/egyfincsf/pdf", headers=headers)
    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"] == "application/pdf"

    pdf_bytes = response.content
    assert bytes(pdf_bytes).startswith(b"%PDF-")

    # verify signature
    with open(tmp_path / "test.pdf", "wb") as f:
        f.write(pdf_bytes)

    from cherenkov.compliance.pdf_renderer import verify_pdf_signature

    sig_info = verify_pdf_signature(str(tmp_path / "test.pdf"))
    assert sig_info["sha256"] is not None
    assert sig_info["sha256"] == response.headers["X-SHA256"]
