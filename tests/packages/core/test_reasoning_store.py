import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from cherenkov.core.reasoning_store import ReasoningStore
from cherenkov.core.schemas.reasoning_trace import ReasoningTrace


@pytest.fixture
def store(tmp_path: Path) -> ReasoningStore:
    db_path = tmp_path / "test_reasoning.db"
    return ReasoningStore(db_path)


def create_mock_trace(
    agent_id: str = "agent-1",
    session_id: str = "session-1",
    step_index: int = 0,
    trace_id: str | None = None,
) -> ReasoningTrace:
    trace_id = trace_id or str(uuid.uuid4())

    trace_data = {
        "trace_id": trace_id,
        "agent_id": agent_id,
        "agent_role": "planner",
        "session_id": session_id,
        "step_index": step_index,
        "step_type": "plan",
        "input_summary": "scrubbed input",
        "output_summary": "scrubbed output",
        "reasoning": "Test reasoning",
        "confidence": 0.95,
        "model_backend": "test_model",
        "latency_ms": 100,
        "tool_name": "test_tool",
        "tool_args_hash": "hash_args",
        "timestamp": datetime.now(timezone.utc),
    }

    # We need to construct the model to compute the hash
    trace_without_anchor = ReasoningTrace(
        **trace_data,
        sha256_anchor="dummy",
    )

    anchor = trace_without_anchor.compute_hash()

    return ReasoningTrace(
        **trace_data,
        sha256_anchor=anchor,
    )


def test_wal_mode_configured(store: ReasoningStore):
    with sqlite3.connect(store.db_path) as conn:
        cursor = conn.execute("PRAGMA journal_mode;")
        row = cursor.fetchone()
        assert row[0].lower() == "wal"


def test_record_and_query_trace(store: ReasoningStore):
    trace = create_mock_trace(agent_id="agent-test", session_id="session-test")

    # Record trace
    store.record(trace)

    # Query trace
    results = store.query(agent_id="agent-test")
    assert len(results) == 1
    retrieved = results[0]

    assert retrieved.trace_id == trace.trace_id
    assert retrieved.agent_id == trace.agent_id
    assert retrieved.session_id == trace.session_id
    assert retrieved.sha256_anchor == trace.sha256_anchor

    # Verify retrieved object hash logic still holds
    assert retrieved.verify_anchor()


def test_query_filtering(store: ReasoningStore):
    trace1 = create_mock_trace(agent_id="agent-1", session_id="session-1")
    trace2 = create_mock_trace(agent_id="agent-1", session_id="session-2")
    trace3 = create_mock_trace(agent_id="agent-2", session_id="session-1")

    store.record(trace1)
    store.record(trace2)
    store.record(trace3)

    # Query by agent
    results = store.query(agent_id="agent-1")
    assert len(results) == 2
    assert {r.session_id for r in results} == {"session-1", "session-2"}

    # Query by session
    results = store.query(session_id="session-1")
    assert len(results) == 2
    assert {r.agent_id for r in results} == {"agent-1", "agent-2"}

    # Query by both
    results = store.query(agent_id="agent-1", session_id="session-1")
    assert len(results) == 1
    assert results[0].trace_id == trace1.trace_id


def test_reject_tampered_trace(store: ReasoningStore):
    trace = create_mock_trace()

    # Tamper with the trace
    trace.reasoning = "Tampered reasoning"

    # Recording should fail because sha256_anchor no longer matches
    with pytest.raises(ValueError, match="failed signature verification"):
        store.record(trace)


def test_export_jsonl(store: ReasoningStore, tmp_path: Path):
    trace1 = create_mock_trace(session_id="session-export", step_index=1)
    trace2 = create_mock_trace(session_id="session-export", step_index=2)
    trace_other = create_mock_trace(session_id="session-other", step_index=1)

    store.record(trace2)
    store.record(trace_other)
    store.record(trace1)

    export_path = tmp_path / "export.jsonl"
    store.export_jsonl("session-export", export_path)

    assert export_path.exists()

    with open(export_path, "r") as f:
        lines = f.readlines()

    assert len(lines) == 2

    # Check ordering (should be sorted by step_index/timestamp)
    parsed_traces = [json.loads(line) for line in lines]
    assert parsed_traces[0]["step_index"] == 1
    assert parsed_traces[1]["step_index"] == 2
    assert parsed_traces[0]["trace_id"] == trace1.trace_id
    assert parsed_traces[1]["trace_id"] == trace2.trace_id