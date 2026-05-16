import json
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cherenkov.core.exceptions import StorageError

logger = logging.getLogger(__name__)

_DB_PATH = Path.home() / ".cherenkov" / "results.db"

_DDL = """
CREATE TABLE IF NOT EXISTS scans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id     TEXT    NOT NULL UNIQUE,
    target      TEXT    NOT NULL,
    started_at  TEXT    NOT NULL,
    finished_at TEXT,
    status      TEXT    NOT NULL DEFAULT 'running',
    findings    TEXT    NOT NULL DEFAULT '[]',
    meta        TEXT    NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_scans_started ON scans(started_at);
CREATE INDEX IF NOT EXISTS idx_scans_target  ON scans(target);

CREATE TABLE IF NOT EXISTS findings_pending (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_id  TEXT    NOT NULL UNIQUE,
    severity    TEXT    NOT NULL,
    scanner     TEXT    NOT NULL,
    title       TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'pending',
    operator_id TEXT,
    approved_at TEXT,
    scan_id     TEXT
);
CREATE INDEX IF NOT EXISTS idx_findings_pending_status ON findings_pending(status);

CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,
    role        INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
"""


def _connect(path: Path = _DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(path: Path = _DB_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as conn:
        conn.executescript(_DDL)


def save_scan(
    scan_id: str,
    target: str,
    findings: list,
    meta: dict | None = None,
    status: str = "done",
    started_at: str | None = None,
    finished_at: str | None = None,
    path: Path = _DB_PATH,
) -> None:
    # WORM enforcement: scan records are forensic evidence and must never be overwritten.
    # Raise StorageError if a record with this scan_id already exists.
    now = datetime.now(timezone.utc).isoformat()
    with _connect(path) as conn:
        existing = conn.execute("SELECT 1 FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
        if existing is not None:
            logger.error(
                "WORM violation: attempted overwrite of immutable scan record scan_id=%s", scan_id
            )
            raise StorageError(
                f"WORM violation: scan record '{scan_id}' already exists and cannot be overwritten."
            )
        conn.execute(
            """
            INSERT INTO scans (scan_id, target, started_at, finished_at, status, findings, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scan_id,
                target,
                started_at or now,
                finished_at or now,
                status,
                json.dumps(findings),
                json.dumps(meta or {}),
            ),
        )


def get_scan(scan_id: str, path: Path = _DB_PATH) -> dict | None:
    with _connect(path) as conn:
        row = conn.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def list_scans(limit: int = 20, path: Path = _DB_PATH) -> list[dict]:
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM scans ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def prune_old_scans(days: int = 90, path: Path = _DB_PATH) -> int:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with _connect(path) as conn:
        cur = conn.execute("DELETE FROM scans WHERE started_at < ?", (cutoff,))
        return cur.rowcount


def save_pending_finding(
    finding_id: str,
    severity: str,
    scanner: str,
    title: str,
    scan_id: str | None = None,
    path: Path = None,
) -> None:
    path = path or _DB_PATH
    with _connect(path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO findings_pending (finding_id, severity, scanner, title, scan_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (finding_id, severity, scanner, title, scan_id),
        )
        conn.commit()


def get_pending_findings(path: Path = None) -> list[dict]:
    path = path or _DB_PATH
    with _connect(path) as conn:
        rows = conn.execute("SELECT * FROM findings_pending WHERE status = 'pending'").fetchall()
    return [dict(r) for r in rows]


def update_finding_status(
    finding_id: str,
    status: str,
    operator_id: str | None = None,
    path: Path = None,
) -> None:
    path = path or _DB_PATH
    now = datetime.now(timezone.utc).isoformat() if status == "approved" else None
    with _connect(path) as conn:
        conn.execute(
            """
            UPDATE findings_pending
            SET status = ?, operator_id = ?, approved_at = ?
            WHERE finding_id = ?
            """,
            (status, operator_id, now, finding_id),
        )
        conn.commit()


def save_user(username: str, hashed_password: str, role: int, path: Path = _DB_PATH) -> None:
    with _connect(path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, role),
        )


def get_user(username: str, path: Path = _DB_PATH) -> dict | None:
    with _connect(path) as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return dict(row) if row else None


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["findings"] = json.loads(d["findings"])
    d["meta"] = json.loads(d["meta"])
    return d
