import pytest
from cherenkov.core.storage.database import (
    get_audit_log,
    get_scan,
    get_tokamak_trace,
    init_db,
    list_scans,
    prune_old_scans,
    save_scan,
    save_scan_trace,
    save_tokamak_trace,
)


@pytest.fixture()
def db(tmp_path):
    path = tmp_path / "test_results.db"
    init_db(path)
    return path


def test_save_and_get_scan(db):
    save_scan(
        "scan-001",
        "http://example.com",
        [{"cwe": "CWE-79", "severity": "HIGH"}],
        meta={"scanner": "header_scanner"},
        path=db,
    )
    result = get_scan("scan-001", path=db)
    assert result is not None
    assert result["target"] == "http://example.com"
    assert result["findings"][0]["cwe"] == "CWE-79"
    assert result["meta"]["scanner"] == "header_scanner"


def test_list_scans_returns_most_recent_first(db):
    for i in range(5):
        save_scan(f"scan-{i:03d}", f"http://target-{i}.com", [], path=db)
    rows = list_scans(limit=3, path=db)
    assert len(rows) == 3
    # most recent inserted last → highest scan_id should be first
    assert rows[0]["scan_id"] == "scan-004"


def test_prune_old_scans_removes_stale_rows(db):
    from datetime import datetime, timedelta, timezone

    old_ts = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
    save_scan("old-scan", "http://old.com", [], started_at=old_ts, finished_at=old_ts, path=db)
    save_scan("new-scan", "http://new.com", [], path=db)

    deleted = prune_old_scans(days=90, path=db)
    assert deleted == 1
    assert get_scan("old-scan", path=db) is None
    assert get_scan("new-scan", path=db) is not None


def test_get_scan_missing_record(db):
    # Ensure that getting a scan that doesn't exist returns None
    result = get_scan("non-existent-scan", path=db)
    assert result is None


def test_save_scan_trace(db):
    scan_id = "test-scan-123"
    trace_hash = "abc123trace"
    scan_result = {"status": "done", "count": 5}
    save_scan_trace(scan_id, trace_hash, scan_result, path=db)

    audit = get_audit_log(limit=1, path=db)
    assert len(audit) == 1
    assert audit[0]["event_type"] == "scan_trace"
    assert audit[0]["user_id"] == scan_id
    assert audit[0]["trace_hash"] == trace_hash
    assert audit[0]["details"] == scan_result


def test_save_and_get_tokamak_trace(db):
    from datetime import datetime, timezone
    finding_id = "fid-999"
    exploit_command = "curl http://internal"
    stdout = "root:x:0:0"
    stderr = ""
    exit_code = 0
    trace_hash = "hash-999"
    ts = datetime.now(timezone.utc).isoformat()
    receipt = {"shredded": True}

    save_tokamak_trace(
        finding_id, exploit_command, stdout, stderr, exit_code,
        trace_hash, ts, receipt, path=db
    )

    trace = get_tokamak_trace(finding_id, path=db)
    assert trace is not None
    assert trace["finding_id"] == finding_id
    assert trace["stdout"] == stdout
    assert trace["trace_hash"] == trace_hash
    assert trace["shred_receipt"] == receipt


def test_save_tokamak_trace_worm_violation(db):
    from cherenkov.core.exceptions import StorageError
    from datetime import datetime, timezone
    finding_id = "fid-worm"
    save_tokamak_trace(finding_id, "cmd", "out", "err", 0, "hash1", datetime.now(timezone.utc).isoformat(), {}, path=db)

    with pytest.raises(StorageError, match="WORM violation"):
        save_tokamak_trace(finding_id, "cmd", "out", "err", 0, "hash2", datetime.now(timezone.utc).isoformat(), {}, path=db)
