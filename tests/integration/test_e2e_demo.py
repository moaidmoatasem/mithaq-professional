import asyncio
import os
import sqlite3
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

import cherenkov.core.storage.database as db
from cherenkov.api.main import app
from cherenkov.core.storage.database import init_db
from cherenkov.compliance.pdf_renderer import verify_pdf_signature
from cherenkov.cli.main import app as cli_app

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def bypass_rate_limit():
    app.state.limiter.enabled = False
    yield
    app.state.limiter.enabled = True


@pytest.fixture(autouse=True)
def mock_jwt_secret(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CHERENKOV_JWT_SECRET=super_secret_test_key_1234567890\n")
    monkeypatch.setenv("ROTATION_ENV_PATH", str(env_file))
    yield


@pytest.fixture(autouse=True)
def isolate_db(tmp_path):
    test_db = tmp_path / "test_api.db"
    
    original_connect = sqlite3.connect
    
    def mock_connect(database, *args, **kwargs):
        # Redirect all cherenkov SQLite connects to the isolated test database
        if isinstance(database, (str, os.PathLike)) and ("results.db" in str(database) or "test_api.db" in str(database) or "cherenkov.db" in str(database)):
            return original_connect(str(test_db), *args, **kwargs)
        return original_connect(database, *args, **kwargs)

    with patch("sqlite3.connect", side_effect=mock_connect):
        init_db(test_db)
        from cherenkov.api.middleware.auth import hash_password
        db.save_user("admin", hash_password("admin"), 3, path=test_db)
        yield


@pytest.fixture(autouse=True)
def mock_external_deps(monkeypatch):
    async def mock_ollama():
        return "online"

    async def mock_qdrant():
        return "online"

    monkeypatch.setattr("cherenkov.api.main._check_ollama", mock_ollama)
    monkeypatch.setattr("cherenkov.api.main._check_qdrant", mock_qdrant)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_e2e_scan_compliance_pdf_flow(client, tmp_path):
    # 1. Authenticate to get a token
    auth_data = {"username": "admin", "password": "admin"}
    token_response = client.post("/api/v1/auth/token", json=auth_data)
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup a simulated scan with findings in the test database
    scan_id = "dvwa-scan-999"
    target_url = "http://dvwa.local"
    findings = [
        {
            "scanner": "SQLInjectionScanner",
            "title": "SQL Injection in DVWA login page",
            "severity": "CRITICAL",
            "cwe": "CWE-89",
            "description": "SQL command injection in user input fields",
            "remediation": "Use parameterized queries or prepared statements",
        }
    ]
    
    # We must patch sqlite3.connect inside the test execution context too to ensure DB operations use the same isolated DB
    test_db = tmp_path / "test_api.db"
    original_connect = sqlite3.connect
    def mock_connect(database, *args, **kwargs):
        if isinstance(database, (str, os.PathLike)) and ("results.db" in str(database) or "test_api.db" in str(database) or "cherenkov.db" in str(database)):
            return original_connect(str(test_db), *args, **kwargs)
        return original_connect(database, *args, **kwargs)

    with patch("sqlite3.connect", side_effect=mock_connect):
        db.save_scan(
            scan_id=scan_id,
            target=target_url,
            findings=findings,
            meta={"chk_id": "CHK-999"},
        )

        # 3. Call the compliance PDF generation endpoint for SAMA CSF (or EGY-FIN CSF)
        response = client.get(
            f"/api/v1/scan/{scan_id}/compliance/egyfincsf/pdf",
            headers=headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        
        # 4. Extract PDF bytes and save to a temporary file
        pdf_path = tmp_path / "cherenkov_egyfincsf_dvwa.pdf"
        pdf_path.write_bytes(response.content)

        # 5. Verify the signature of the generated PDF programmatically
        result = verify_pdf_signature(str(pdf_path))
        assert result["valid"] is True
        assert "sha256" in result
        assert result["tsa_status"] in ("ok", "skipped", "unavailable")

        # 6. Verify via the CLI command using CliRunner
        runner = CliRunner()
        cli_result = runner.invoke(cli_app, ["verify", str(pdf_path)])
        assert cli_result.exit_code == 0
        assert "Signature status: VALID" in cli_result.output
        assert "SHA-256 (findings):" in cli_result.output
