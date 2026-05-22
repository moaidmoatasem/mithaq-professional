import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from cherenkov.core.reasoning_store import ReasoningStore


@pytest.fixture
def temp_db_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("cherenkov.core.reasoning_store.Path") as mock_path:
            # We want to use the temp directory to isolate our tests
            mock_path.return_value = Path(tmpdir)
            yield Path(tmpdir)


def test_init_db(temp_db_dir):
    store = ReasoningStore("test_session")
    assert store.db_path.exists()

    # Check that schema was created correctly
    with sqlite3.connect(store.db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ReasoningTrace'"
        )
        assert cursor.fetchone() is not None


def test_query_and_verify(temp_db_dir):
    store = ReasoningStore("test_session")

    agent = "developer-agent-01"
    tool_name = "llm_inference"
    model = "ollama/qwen2.5-coder"
    reasoning = "Test reasoning..."
    duration_ms = 342
    confidence = 0.87
    step_index = 1

    content = (
        f"{step_index}{agent}{tool_name}{model}{duration_ms}{reasoning}{confidence}"
    )
    sha256 = hashlib.sha256(content.encode()).hexdigest()

    with sqlite3.connect(store.db_path) as conn:
        conn.execute(
            "INSERT INTO ReasoningTrace (step_index, agent, tool_name, model, duration_ms, reasoning, confidence, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                step_index,
                agent,
                tool_name,
                model,
                duration_ms,
                reasoning,
                confidence,
                sha256,
            ),
        )

    traces = store.query()
    assert len(traces) == 1
    assert traces[0]["step_index"] == 1
    assert traces[0]["agent"] == agent

    # Verify correctly computed hashes pass
    results = store.verify_hashes()
    assert len(results) == 1
    assert results[0]["status"] == "PASS"

    # Intentionally corrupt the hash
    with sqlite3.connect(store.db_path) as conn:
        conn.execute(
            "UPDATE ReasoningTrace SET reasoning = 'Corrupted reasoning' WHERE step_index = 1"
        )

    # Verify corrupted hash fails
    results = store.verify_hashes()
    assert results[0]["status"] == "FAIL"


def test_export_jsonl(temp_db_dir):
    store = ReasoningStore("test_export")

    step_index = 1
    agent = "test-agent"
    content = f"{step_index}{agent}toolmodel100test1.0"
    sha256 = hashlib.sha256(content.encode()).hexdigest()

    with sqlite3.connect(store.db_path) as conn:
        conn.execute(
            "INSERT INTO ReasoningTrace (step_index, agent, tool_name, model, duration_ms, reasoning, confidence, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (step_index, agent, "tool", "model", 100, "test", 1.0, sha256),
        )

    export_path = temp_db_dir / "export.jsonl"
    store.export_jsonl(str(export_path))

    assert export_path.exists()
    with open(export_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["agent"] == agent
