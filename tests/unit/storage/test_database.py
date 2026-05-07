import pytest
from pathlib import Path
from mithaq.storage.database import init_db, save_scan, get_scan, list_scans, prune_old_scans


@pytest.fixture()
def db(tmp_path):
    path = tmp_path / "test_results.db"
    init_db(path)
    return path


def test_save_and_get_scan(db):
    save_scan("scan-001", "http://example.com", [{"cwe": "CWE-79", "severity": "HIGH"}],
              meta={"scanner": "header_scanner"}, path=db)
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

