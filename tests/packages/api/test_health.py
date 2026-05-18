from unittest.mock import MagicMock, patch

import pytest
from cherenkov.api.main import v1_health
from httpx import RequestError, Response


class MockAsyncClient:
    def __init__(self, ollama_status=200, qdrant_status=200, qdrant_vector_count=0, raise_error=False):
        self.ollama_status = ollama_status
        self.qdrant_status = qdrant_status
        self.qdrant_vector_count = qdrant_vector_count
        self.raise_error = raise_error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get(self, url, **kwargs):
        if self.raise_error:
            raise RequestError("Connection error")
        if "11434/api/tags" in url:
            return Response(self.ollama_status)
        if "6333/health" in url:
            return Response(self.qdrant_status)
        if "6333/collections/cherenkov_findings" in url:
            return Response(200, json={"result": {"vectors_count": self.qdrant_vector_count}})
        return Response(404)

@pytest.fixture
def mock_db_stats():
    with patch("cherenkov.core.storage.database.db_stats", return_value={"size_bytes": 1024}):
        yield

@pytest.fixture
def mock_active_scans():
    with patch("cherenkov.api.main._get_active_scans_count", return_value=2):
        yield

@pytest.fixture
def mock_tokamak_count():
    with patch("cherenkov.api.main._get_tokamak_container_count", return_value=1):
        yield

@pytest.mark.asyncio
async def test_health_healthy(mock_db_stats, mock_active_scans, mock_tokamak_count):
    with patch("httpx.AsyncClient", return_value=MockAsyncClient(qdrant_vector_count=42)):
        res = await v1_health()
        assert res["status"] == "healthy"
        assert res["version"] == "1.1.0"
        assert "timestamp" in res
        assert res["storage"] == {"size_bytes": 1024}
        assert res["queue"]["scan_jobs_pending"] == 2

        nodes = res["nodes"]
        assert nodes["tensor"]["status"] == "ready"
        assert nodes["kinetic"]["status"] == "ready"
        assert nodes["aegis"]["status"] == "ready"
        assert nodes["lattice"]["status"] == "ready"
        assert nodes["lattice"]["vector_count"] == 42
        assert nodes["tokamak"]["status"] == "ready"
        assert nodes["tokamak"]["active_containers"] == 1

@pytest.mark.asyncio
async def test_health_ollama_offline(mock_db_stats, mock_active_scans, mock_tokamak_count):
    with patch("httpx.AsyncClient", return_value=MockAsyncClient(ollama_status=500)):
        res = await v1_health()
        assert res["nodes"]["tensor"]["status"] == "offline"
        assert res["nodes"]["kinetic"]["status"] == "offline"
        assert res["nodes"]["aegis"]["status"] == "offline"
        assert res["nodes"]["lattice"]["status"] == "ready"

@pytest.mark.asyncio
async def test_health_qdrant_offline(mock_db_stats, mock_active_scans, mock_tokamak_count):
    with patch("httpx.AsyncClient", return_value=MockAsyncClient(qdrant_status=500)):
        res = await v1_health()
        assert res["nodes"]["tensor"]["status"] == "ready"
        assert res["nodes"]["lattice"]["status"] == "offline"

@pytest.mark.asyncio
async def test_health_http_error(mock_db_stats, mock_active_scans, mock_tokamak_count):
    with patch("httpx.AsyncClient", return_value=MockAsyncClient(raise_error=True)):
        res = await v1_health()
        assert res["nodes"]["tensor"]["status"] == "offline"
        assert res["nodes"]["lattice"]["status"] == "offline"
        assert res["nodes"]["lattice"]["vector_count"] == 0
