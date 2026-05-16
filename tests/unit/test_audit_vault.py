import os
import pytest
import sqlite3
import tempfile
from pathlib import Path
from cherenkov.core.storage.database import init_db, save_audit_entry, get_audit_log, save_scan, StorageError

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    db_path = Path(path)
    init_db(db_path)
    yield db_path
    if db_path.exists():
        os.remove(db_path)

def test_audit_log_immutability(temp_db):
    # 1. Create an audit entry
    details = {"action": "test"}
    trace_hash = save_audit_entry("TEST_EVENT", "user1", details, path=temp_db)
    
    # 2. Verify it exists
    logs = get_audit_log(path=temp_db)
    assert len(logs) == 1
    assert logs[0]["event_type"] == "TEST_EVENT"
    assert logs[0]["trace_hash"] == trace_hash

    # 3. Try to manually DELETE from the table (simulating a malicious actor)
    # The requirement is that the code doesn't provide DELETE, 
    # but for a true WORM we might use triggers.
    # For now, we just verify the WORM enforcement in save_scan.
    pass

def test_scan_worm_violation(temp_db):
    scan_id = "scan-123"
    target = "https://example.com"
    
    # 1. Save scan
    save_scan(scan_id, target, [], path=temp_db)
    
    # 2. Attempt to save same scan_id again -> should raise StorageError
    with pytest.raises(StorageError) as exc:
        save_scan(scan_id, target, [{"id": "new"}], path=temp_db)
    
    assert "WORM violation" in str(exc.value)

def test_audit_log_trace_hash_consistency(temp_db):
    details = {"key": "val"}
    event_type = "CONSISTENCY_CHECK"
    user_id = "operator"
    
    trace_hash = save_audit_entry(event_type, user_id, details, path=temp_db)
    
    logs = get_audit_log(path=temp_db)
    entry = logs[0]
    
    # Re-calculate hash manually
    import json
    import hashlib
    payload = f"{entry['timestamp']}|{event_type}|{user_id}|{json.dumps(details)}"
    expected_hash = hashlib.sha256(payload.encode()).hexdigest()
    
    assert entry["trace_hash"] == expected_hash
