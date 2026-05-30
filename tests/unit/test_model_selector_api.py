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




"""Unit tests for model selector API endpoints."""

import os
from unittest.mock import patch

import pytest
from cherenkov.api.main import app
from cherenkov.api.middleware.auth import Role, User
from fastapi.testclient import TestClient

os.environ.setdefault("CHERENKOV_JWT_SECRET", "test-secret-for-model-selector-api")


@pytest.fixture(autouse=True)
def _override_auth():
    async def mock_user() -> User:
        return User(username="test_operator", role=Role.OPERATOR)

    from cherenkov.api.middleware.auth import get_current_user

    app.dependency_overrides[get_current_user] = mock_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestModelRecommend:
    def test_returns_recommendations(self, client):
        with patch("cherenkov.api.main.detect_hardware") as mock_detect:
            mock_detect.return_value = {
                "ram_gb": 16.0,
                "cpu_cores": 8,
                "platform": "Linux",
                "vram_gb": 6.0,
                "has_gpu": True,
                "gpu_name": "RTX 3060",
                "tier": "medium",
            }
            resp = client.get("/api/v1/models/recommend")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "medium"
        assert "hardware" in data
        assert "selected" in data
        assert "pull_commands" in data
        assert len(data["pull_commands"]) > 0

    def test_recommend_low_end(self, client):
        with patch("cherenkov.api.main.detect_hardware") as mock_detect:
            mock_detect.return_value = {
                "ram_gb": 4.0,
                "cpu_cores": 2,
                "platform": "Linux",
                "vram_gb": 0.0,
                "has_gpu": False,
                "gpu_name": "None",
                "tier": "low",
            }
            resp = client.get("/api/v1/models/recommend")
        assert resp.status_code == 200
        assert resp.json()["tier"] == "low"


class TestModelLiteLLMConfig:
    def test_returns_config(self, client):
        with patch("cherenkov.api.main.recommend_models") as mock_recs:
            mock_recs.return_value = {
                "tier": "medium",
                "effective_memory_gb": 6.4,
                "hardware": {"tier": "medium"},
                "selected": {
                    "embed": {
                        "name": "embed",
                        "model": "nomic-embed-text",
                        "size_gb": 0.3,
                        "description": "test",
                    },
                    "code": {
                        "name": "code-smart",
                        "model": "qwen2.5-coder:7b",
                        "size_gb": 5.0,
                        "description": "test",
                    },
                },
                "pull_commands": ["ollama pull nomic-embed-text"],
                "advice": "Test",
            }
            resp = client.get("/api/v1/models/litellm-config")
        assert resp.status_code == 200
        data = resp.json()
        assert "config" in data
        assert "apply_command" in data
        assert "ollama/nomic-embed-text" in data["config"]
        assert "ollama/qwen2.5-coder:7b" in data["config"]


class TestModelAvailable:
    def test_ollama_offline(self, client):
        resp = client.get("/api/v1/models/available")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"models": [], "error": "Ollama not reachable"}
