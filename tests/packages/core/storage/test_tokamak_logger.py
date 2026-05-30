import logging
import sqlite3
from pathlib import Path

import pytest
from cherenkov.core.storage.tokamak_logger import TokamakLogger


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    # We place the db in a subdirectory to ensure directory creation works
    return tmp_path / "subdir" / "tokamak_logs.db"


@pytest.fixture()
def logger_instance(db_path: Path) -> TokamakLogger:
    return TokamakLogger(db_path=db_path)


def test_tokamak_logger_initialization_creates_dir(db_path: Path):
    assert not db_path.exists()
    _ = TokamakLogger(db_path=db_path)
    assert db_path.exists()

    # Check that PRAGMA journal_mode=wal is set
    with sqlite3.connect(db_path) as conn:
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        # WAL mode can return 'wal' or 'WAL'
        assert mode.lower() == "wal"


def test_log_execution_inserts_record_and_returns_hash(logger_instance: TokamakLogger, caplog):
    caplog.set_level(logging.INFO)

    trace_hash = logger_instance.log_execution(
        target="http://example.com", payload="echo 1", stdout="1", stderr="", exit_code=0
    )

    # trace_hash is a full SHA-256 (64 characters)
    assert len(trace_hash) == 64

    # Ensure log output truncates hash to 8 characters per security rules
    short_hash = trace_hash[:8]
    log_messages = [r.message for r in caplog.records]
    assert any(f"hash_anchor={short_hash}" in msg for msg in log_messages)
    assert not any(trace_hash in msg for msg in log_messages)

    # Verify the record was inserted
    logs = logger_instance.get_logs()
    assert len(logs) == 1
    assert logs[0]["target"] == "http://example.com"
    assert logs[0]["payload"] == "echo 1"
    assert logs[0]["stdout"] == "1"
    assert logs[0]["stderr"] == ""
    assert logs[0]["exit_code"] == 0
    assert logs[0]["trace_hash"] == trace_hash


def test_get_logs_filtering(logger_instance: TokamakLogger):
    logger_instance.log_execution("http://a.com", "payload a", "out a", "", 0)
    logger_instance.log_execution("http://b.com", "payload b", "out b", "", 0)
    logger_instance.log_execution("http://a.com", "payload c", "out c", "", 1)

    all_logs = logger_instance.get_logs()
    assert len(all_logs) == 3

    a_logs = logger_instance.get_logs(target="http://a.com")
    assert len(a_logs) == 2
    assert all(log["target"] == "http://a.com" for log in a_logs)

    # Order should be DESC
    assert a_logs[0]["payload"] == "payload c"
    assert a_logs[1]["payload"] == "payload a"


def test_log_execution_raises_on_db_error(logger_instance: TokamakLogger, tmp_path: Path):
    # Swap out db path to a directory instead of a file to force sqlite error
    logger_instance.db_path = tmp_path

    with pytest.raises(sqlite3.Error):
        logger_instance.log_execution("target", "payload", "out", "err", 1)
