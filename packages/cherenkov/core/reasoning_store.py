import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List


class ReasoningStore:
    """Store for human-readable reasoning logs of agent actions."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        # Explicit path handling per task definition
        self.db_path = Path("data") / "reasoning" / f"{session_id}.db"
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database and schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ReasoningTrace (
                    step_index INTEGER PRIMARY KEY,
                    agent TEXT,
                    tool_name TEXT,
                    model TEXT,
                    duration_ms INTEGER,
                    reasoning TEXT,
                    confidence REAL,
                    sha256 TEXT
                )
            """)

    def query(self) -> List[Dict[str, Any]]:
        """Retrieve all traces ordered by step_index."""
        if not self.db_path.exists():
            return []

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM ReasoningTrace ORDER BY step_index ASC"
            )
            return [dict(row) for row in cursor.fetchall()]

    def export_jsonl(self, out_path: str) -> None:
        """Export all traces to a JSONL file."""
        traces = self.query()
        with open(out_path, "w", encoding="utf-8") as f:
            for trace in traces:
                f.write(json.dumps(trace) + "\n")

    def verify_hashes(self) -> List[Dict[str, Any]]:
        """
        Verify cryptographic hashes of all traces.
        Returns a list of dicts with verification results per row.
        """
        traces = self.query()
        results = []
        for trace in traces:
            content_to_hash = f"{trace['step_index']}{trace['agent']}{trace['tool_name']}{trace['model']}{trace['duration_ms']}{trace['reasoning']}{trace['confidence']}"
            expected_hash = hashlib.sha256(content_to_hash.encode()).hexdigest()
            status = "PASS" if trace["sha256"] == expected_hash else "FAIL"
            results.append(
                {
                    "step_index": trace["step_index"],
                    "status": status,
                    "stored": trace["sha256"],
                    "recomputed": expected_hash,
                }
            )
        return results
