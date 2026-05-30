import sys
from unittest.mock import MagicMock

class MockPsutil:
    def __init__(self):
        self.__spec__ = MagicMock()
    def cpu_count(self, logical=False):
        return 8
    def virtual_memory(self):
        class Mem:
            total = 16e9
        return Mem()
sys.modules['psutil'] = MockPsutil()




import os
import tempfile

import pytest

pytestmark = pytest.mark.integration

from cherenkov.api.main import app
from cherenkov.credentials import DefaultCredentialsManager
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def isolated_env(tmp_path):
    """Isolate rotation env for each test."""
    env_path = tmp_path / ".cherenkov" / ".env"
    env_path.parent.mkdir(parents=True)
    env_path.write_text("CHERENKOV_JWT_SECRET=\n")
    os.environ["ROTATION_ENV_PATH"] = str(env_path)
    os.environ["CHERENKOV_DB_PATH"] = str(tmp_path / "results.db")
    yield
    os.environ.pop("ROTATION_ENV_PATH", None)


@pytest.mark.integration
def test_rotation_required_on_fresh_install():
    client = TestClient(app, raise_server_exceptions=False)
    # /health is accessible
    r = client.get("/health")
    assert r.status_code == 200
    # /api/v1/scan is blocked
    r = client.post("/api/v1/scan", json={"url": "http://example.com"})
    assert r.status_code in [423, 401]
    if r.status_code == 423:
        assert "rotation_required" in r.json().get("detail", "")


@pytest.mark.integration
def test_rotate_password_clears_flag(tmp_path):
    DefaultCredentialsManager.set_rotation_flag()
    assert DefaultCredentialsManager.is_rotation_required() is True
    DefaultCredentialsManager.clear_rotation_flag()
    assert DefaultCredentialsManager.is_rotation_required() is False


@pytest.mark.integration
def test_rotate_password_success(tmp_path):
    from cherenkov.api.middleware.auth import hash_password
    from cherenkov.core.storage.database import init_db, save_user

    init_db()
    save_user("admin", hash_password("oldsecret"), 3)  # ADMIN
    DefaultCredentialsManager.set_rotation_flag()
    env = tmp_path / ".cherenkov" / ".env"
    env.parent.mkdir(parents=True, exist_ok=True)
    env.write_text("CHERENKOV_JWT_SECRET=testsecret123\n")
    os.environ["ROTATION_ENV_PATH"] = str(env)

    client = TestClient(app, raise_server_exceptions=False)
    # Login
    r = client.post("/api/v1/auth/token", json={"username": "admin", "password": "oldsecret"})
    assert r.status_code == 200
    # Rotate
    token = r.json().get("access_token")
    client.cookies.set("session", token)
    r = client.post(
        "/api/v1/auth/rotate-password",
        json={"old_password": "oldsecret", "new_password": "newsecret"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
