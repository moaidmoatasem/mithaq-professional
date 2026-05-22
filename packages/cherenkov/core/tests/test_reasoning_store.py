from pathlib import Path

import pytest
from cherenkov.core.reasoning.reasoning_store import ReasoningStore, ReasoningTrace


def test_reasoning_store(tmp_path: Path, capsys):
    db_path = tmp_path / "test_session.db"
    store = ReasoningStore(db_path=db_path)

    trace1 = ReasoningTrace(
        session_id="test_session",
        trace_id="trace_1",
        agent_id="agent_1",
        action="action_1",
        details={"key": "value1"},
    )
    store.append_trace(trace1)

    store2 = ReasoningStore(db_path=db_path)
    traces = store2.query()
    assert len(traces) == 1
    assert traces[0].trace_id == "trace_1"

    store2.verify("test_session")
    captured = capsys.readouterr()
    assert "[PASS] Step 00" in captured.out

    # Tamper test
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE traces SET details='{}' WHERE trace_id='trace_1'")
        conn.commit()

    store3 = ReasoningStore(db_path=db_path)
    store3.verify("test_session")
    captured_tamper = capsys.readouterr()
    assert "[FAIL] Step 00" in captured_tamper.out
    assert "Tamper detected: 1 of 1 steps failed anchor verification." in captured_tamper.out
