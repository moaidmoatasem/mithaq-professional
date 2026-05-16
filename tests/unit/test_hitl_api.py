import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi import Depends

from cherenkov.api.main import app, _broadcast
from cherenkov.api.middleware.auth import User, Role
from cherenkov.core.storage.database import (
    init_db,
    save_pending_finding,
    get_pending_findings,
    update_finding_status,
)


_override_user = User(username="test_operator", role=Role.OPERATOR)


async def _override_get_current_user(authorization=None) -> User:
    return _override_user


def _override_role_checker(required_role: Role):
    def checker(user: User = Depends(_override_get_current_user)):
        return user

    return checker


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path: Path) -> None:
    from cherenkov.core.storage import database as db

    db._DB_PATH = tmp_path / ".cherenkov" / "results.db"
    db.init_db(db._DB_PATH)


@pytest.fixture(autouse=True)
def _override_auth():
    from cherenkov.api.main import v1
    from cherenkov.api.middleware.auth import get_current_user

    app.dependency_overrides[get_current_user] = _override_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seed_pending():
    save_pending_finding("finding-1", "CRITICAL", "xss", "XSS Found", scan_id="scan-1")
    save_pending_finding("finding-2", "HIGH", "sqli", "SQL Injection", scan_id="scan-1")
    save_pending_finding("finding-3", "MEDIUM", "cors", "CORS Misconfig", scan_id="scan-1")


class TestGetPendingFindings:
    def test_no_pending_returns_empty_list(self, client: TestClient):
        resp = client.get("/api/v1/findings/pending")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_pending_findings(self, client: TestClient, seed_pending):
        resp = client.get("/api/v1/findings/pending")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

        finding_ids = {r["finding_id"] for r in data}
        assert "finding-1" in finding_ids
        assert "finding-2" in finding_ids
        assert "finding-3" in finding_ids

        for r in data:
            assert r["status"] == "pending"

    def test_approved_not_returned(self, client: TestClient, seed_pending):
        update_finding_status("finding-1", "approved", "test_op")
        resp = client.get("/api/v1/findings/pending")
        data = resp.json()
        assert len(data) == 2
        assert all(r["finding_id"] != "finding-1" for r in data)


class TestApproveFinding:
    def test_approve_updates_status(self, client: TestClient, seed_pending):
        resp = client.post("/api/v1/findings/finding-1/approve")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["finding_id"] == "finding-1"
        assert body["new_status"] == "approved"

    def test_approve_persists(self, client: TestClient, seed_pending):
        client.post("/api/v1/findings/finding-1/approve")
        pending = get_pending_findings()
        assert all(r["finding_id"] != "finding-1" for r in pending)

    def test_approve_nonexistent_does_not_error(self, client: TestClient):
        resp = client.post("/api/v1/findings/nonexistent-id/approve")
        assert resp.status_code == 200


class TestRejectFinding:
    def test_reject_updates_status(self, client: TestClient, seed_pending):
        resp = client.post("/api/v1/findings/finding-1/reject")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["finding_id"] == "finding-1"
        assert body["new_status"] == "rejected"

    def test_reject_removes_from_pending(self, client: TestClient, seed_pending):
        client.post("/api/v1/findings/finding-1/reject")
        pending = get_pending_findings()
        assert all(r["finding_id"] != "finding-1" for r in pending)

    def test_reject_then_approve_allows_flow(self, client: TestClient, seed_pending):
        client.post("/api/v1/findings/finding-1/reject")
        resp = client.post("/api/v1/findings/finding-1/approve")
        assert resp.status_code == 200
