import pytest
import sqlite3
import json
import os
import hashlib
from fastapi.testclient import TestClient
from cherenkov.api.main import app, _DB_PATH

client = TestClient(app)

@pytest.mark.integration
def test_e2e_demo_scan_compliance_pdf():
    # Setup dummy user to pass authentication
    from cherenkov.api.middleware.auth import create_access_token
    from cherenkov.core.storage.database import init_db

    # ensure db is fully initialized with all tables
    init_db()

    token = create_access_token({"sub": "admin", "role": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Setup a dummy scan record
    scan_id = "test-e2e-scan"

    findings = [
        {
            "id": "1",
            "title": "SQL Injection",
            "severity": "CRITICAL",
            "description": "SQL injection vulnerability found.",
            "cwe": "CWE-89",
            "remediation": "Use prepared statements",
            "scanner": "sqli_scanner"
        }
    ]

    db_path = _DB_PATH
    os.makedirs(db_path.parent, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
        conn.execute(
            "INSERT INTO scans (scan_id, target, status, started_at, finished_at, findings, meta) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (scan_id, "http://localhost:80", "completed", "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z", json.dumps(findings), json.dumps({"chk_id": "CHK-TEST"}))
        )

    # 2. Get PDF - the route is mounted with prefix "/api/v1" under `v1` which is included without prefix,
    # but the method says @v1.get("/scan/{scan_id}/compliance/{fw}/pdf") so it should be /api/v1/scan...
    # Let me grep where v1 is defined
    resp = client.get(f"/api/v1/scan/{scan_id}/compliance/egyfincsf/pdf", headers=headers)

    print(resp.json() if resp.status_code != 200 else "OK")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/pdf"
    assert "cherenkov_EGYFINCSF_test-e2e-scan.pdf" in resp.headers["Content-Disposition"]

    pdf_content = resp.content

    import tempfile

    # Write to file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    from cherenkov.compliance.pdf_renderer import verify_pdf_signature
    verification = verify_pdf_signature(tmp_path)
    os.remove(tmp_path)
    assert verification["valid"] is True
    assert "sha256" in verification
