import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from cherenkov.core.storage.database import (
    StorageError,
    _connect,
    get_trace,
    init_db,
    save_trace,
)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    db_path = Path(path)
    init_db(db_path)
    yield db_path
    if db_path.exists():
        os.remove(db_path)


def test_db_is_wal_mode(temp_db):
    """Confirm the database connection is initialized in WAL mode."""
    conn = _connect(temp_db)
    cursor = conn.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    conn.close()
    assert mode.lower() == "wal"


def test_save_and_get_trace(temp_db):
    """Verify trace records persist and retrieve deterministically."""
    finding_id = "test-finding-123"
    exploit_command = "echo 'poc'"
    stdout = "poc"
    stderr = ""
    exit_code = 0
    trace_hash = "abc123hash"
    timestamp = datetime.now(timezone.utc).isoformat()
    shred_receipt = {"files_erased": ["payload.sh"], "method": "overwrite"}

    save_trace(
        finding_id=finding_id,
        exploit_command=exploit_command,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        trace_hash=trace_hash,
        timestamp=timestamp,
        shred_receipt=shred_receipt,
        path=temp_db,
    )

    trace = get_trace(finding_id, path=temp_db)
    assert trace is not None
    assert trace["finding_id"] == finding_id
    assert trace["exploit_command"] == exploit_command
    assert trace["stdout"] == stdout
    assert trace["stderr"] == stderr
    assert trace["exit_code"] == exit_code
    assert trace["trace_hash"] == trace_hash
    assert trace["timestamp"] == timestamp
    assert trace["shred_receipt"] == shred_receipt


def test_trace_worm_violation(temp_db):
    """Verify WORM enforcement: existing traces cannot be overwritten."""
    finding_id = "immutable-finding"
    exploit_command = "exit 0"
    stdout = ""
    stderr = ""
    exit_code = 0
    trace_hash = "hash1"
    timestamp = datetime.now(timezone.utc).isoformat()
    shred_receipt = {}

    save_trace(
        finding_id=finding_id,
        exploit_command=exploit_command,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        trace_hash=trace_hash,
        timestamp=timestamp,
        shred_receipt=shred_receipt,
        path=temp_db,
    )

    # Attempt to overwrite with the same finding_id
    with pytest.raises(StorageError) as exc:
        save_trace(
            finding_id=finding_id,
            exploit_command=exploit_command,
            stdout="new stdout",
            stderr=stderr,
            exit_code=1,
            trace_hash="hash2",
            timestamp=timestamp,
            shred_receipt=shred_receipt,
            path=temp_db,
        )

    assert "WORM violation" in str(exc.value)


def test_trace_hash_uniqueness(temp_db):
    """Verify trace_hash UNIQUE constraint raises sqlite3.IntegrityError."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Save first trace with hash1
    save_trace(
        finding_id="finding1",
        exploit_command="exit 0",
        stdout="",
        stderr="",
        exit_code=0,
        trace_hash="hash1",
        timestamp=timestamp,
        shred_receipt={},
        path=temp_db,
    )

    # Attempt to save second trace with the exact same trace_hash (hash1)
    with pytest.raises(sqlite3.IntegrityError):
        save_trace(
            finding_id="finding2",
            exploit_command="exit 0",
            stdout="",
            stderr="",
            exit_code=0,
            trace_hash="hash1",
            timestamp=timestamp,
            shred_receipt={},
            path=temp_db,
        )
