import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
    now = datetime.now(timezone.utc).isoformat()
    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO scans (scan_id, target, started_at, finished_at, status, findings, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(scan_id) DO UPDATE SET
                finished_at = excluded.finished_at,
                status      = excluded.status,
                findings    = excluded.findings,
                meta        = excluded.meta
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


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["findings"] = json.loads(d["findings"])
    d["meta"] = json.loads(d["meta"])
    return d
