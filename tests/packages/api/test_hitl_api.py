import uuid

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.ai_generated

from cherenkov.api.main import app
from cherenkov.core.storage.database import (
    _DB_PATH,
    _connect,
    init_db,
    save_pending_finding,
    update_finding_status,
)


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_hitl.db"

    # Need to properly patch the globals where they are imported or used
    monkeypatch.setattr("cherenkov.core.storage.database._DB_PATH", db_path)

    # Because FastAPI might use the original default kwargs for init_db,
    # we need to ensure the module-level variable is changed or default args are overridden.
    import cherenkov.core.storage.database as db

    original_db_path = db._DB_PATH
    db._DB_PATH = db_path

    # Re-initialize the db for this specific tmp path
    init_db(db_path)

    # We also need to clear out the db in case of re-use
    with db._connect(db_path) as conn:
        conn.execute("DELETE FROM findings_pending")
        conn.execute("DELETE FROM scans")
        conn.commit()

    yield db_path

    db._DB_PATH = original_db_path

    # cleanup not strictly necessary as tmp_path is managed, but good practice


@pytest.fixture
def client(setup_db):
    # Depending on setup_db to ensure DB is initialized
    return TestClient(app)


def test_get_pending_findings_empty(client):
    response = client.get("/api/v1/findings/pending")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.xfail(reason="Predates JWT auth middleware; needs token fixture — Sprint 4", strict=True)
def test_approve_reject_finding(client, setup_db):
    finding_id = str(uuid.uuid4())
    save_pending_finding(finding_id, "CRITICAL", "TestScanner", "Test Title")

    response = client.get("/api/v1/findings/pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["finding_id"] == finding_id
    assert data[0]["status"] == "pending"

    # Approve
    response = client.post(
        f"/api/v1/findings/{finding_id}/approve", params={"operator_id": "op_123"}
    )
    assert response.status_code == 200
    assert response.json()["new_status"] == "approved"

    # Pending should be empty
    response = client.get("/api/v1/findings/pending")
    assert response.json() == []

    # Check status in db
    with _connect(setup_db) as conn:
        row = conn.execute(
            "SELECT status, operator_id, approved_at FROM findings_pending WHERE finding_id = ?",
            (finding_id,),
        ).fetchone()
        assert row is not None
        assert row["status"] == "approved"
        assert row["operator_id"] == "op_123"
        assert row["approved_at"] is not None

    # Reject
    response = client.post(
        f"/api/v1/findings/{finding_id}/reject", params={"operator_id": "op_456"}
    )
    assert response.status_code == 200
    assert response.json()["new_status"] == "rejected"

    # Check status in db
    with _connect(setup_db) as conn:
        row = conn.execute(
            "SELECT status, operator_id, approved_at FROM findings_pending WHERE finding_id = ?",
            (finding_id,),
        ).fetchone()
        assert row is not None
        assert row["status"] == "rejected"
        assert row["operator_id"] == "op_456"
        assert row["approved_at"] is None


@pytest.mark.xfail(reason="Predates JWT auth middleware; needs token fixture — Sprint 4", strict=True)
def test_run_scan_hitl_integration(client, monkeypatch):
    class MockScanEngine:
        def __init__(self, registry):
            pass

        async def scan_all(self, url, timeout=10.0):
            from cherenkov.core.base_scanner import Finding, ScanResult, Severity

            return {
                "TestScanner": ScanResult(
                    target=url,
                    scanner_name="TestScanner",
                    findings=[
                        Finding(
                            title="Crit",
                            severity=Severity.CRITICAL,
                            description="desc",
                            cwe="cwe",
                            remediation="fix",
                        ),
                        Finding(
                            title="High",
                            severity=Severity.HIGH,
                            description="desc",
                            cwe="cwe",
                            remediation="fix",
                        ),
                        Finding(
                            title="Low",
                            severity=Severity.LOW,
                            description="desc",
                            cwe="cwe",
                            remediation="fix",
                        ),
                    ],
                )
            }

    monkeypatch.setattr("cherenkov.core.engine.ScanEngine", MockScanEngine)

    async def mock_broadcast(event):
        pass

    monkeypatch.setattr("cherenkov.api.main._broadcast", mock_broadcast)

    response = client.post("/api/v1/scan", json={"url": "http://example.com"})
    assert response.status_code == 200

    # Check pending findings
    response = client.get("/api/v1/findings/pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    severities = {f["severity"] for f in data}
    assert severities == {"CRITICAL", "HIGH"}
