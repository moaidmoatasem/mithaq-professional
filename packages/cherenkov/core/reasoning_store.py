import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from cherenkov.core.schemas.reasoning_trace import ReasoningTrace

logger = logging.getLogger(__name__)


class ReasoningStore:
    """SQLite-backed store for ReasoningTrace records."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            # Configure WAL mode and synchronous settings as per TOKAMAK rules
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS reasoning_traces (
                    trace_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    agent_role TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    step_index INT NOT NULL,
                    step_type TEXT NOT NULL,
                    input_summary TEXT NOT NULL,
                    output_summary TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    confidence REAL,
                    model_backend TEXT,
                    latency_ms INT,
                    tool_name TEXT,
                    tool_args_hash TEXT,
                    sha256_anchor TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """)

    def record(self, trace: ReasoningTrace) -> None:
        """Insert one row. Raises if sha256_anchor verification fails."""
        if not trace.verify_anchor():
            raise ValueError(
                f"Trace {trace.trace_id} failed signature verification (tampering detected)."
            )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO reasoning_traces (
                    trace_id, agent_id, agent_role, session_id, step_index, step_type,
                    input_summary, output_summary, reasoning, confidence, model_backend,
                    latency_ms, tool_name, tool_args_hash, sha256_anchor, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace.trace_id,
                    trace.agent_id,
                    trace.agent_role,
                    trace.session_id,
                    trace.step_index,
                    trace.step_type,
                    trace.input_summary,
                    trace.output_summary,
                    trace.reasoning,
                    trace.confidence,
                    trace.model_backend,
                    trace.latency_ms,
                    trace.tool_name,
                    trace.tool_args_hash,
                    trace.sha256_anchor,
                    trace.timestamp.isoformat(),
                ),
            )

        # Explicit requirement: Do NOT expose the raw SQLite file path in any log output
        # log only the SHA-256 anchor.
        logger.info("Recorded reasoning trace anchor: %s", trace.sha256_anchor)

    def query(
        self,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[ReasoningTrace]:
        """Query reasoning traces by agent_id and/or session_id."""
        query = "SELECT * FROM reasoning_traces"
        conditions = []
        params = []

        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        results = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, tuple(params))
            for row in cursor:
                # Reconstruct datetime from ISO format string
                ts_str = row["timestamp"]
                # SQLite sometimes truncates the timezone info, so we handle it gracefully
                if ts_str.endswith("Z"):
                    ts_str = ts_str[:-1] + "+00:00"
                timestamp = datetime.fromisoformat(ts_str)

                trace = ReasoningTrace(
                    trace_id=row["trace_id"],
                    agent_id=row["agent_id"],
                    agent_role=row["agent_role"],
                    session_id=row["session_id"],
                    step_index=row["step_index"],
                    step_type=row["step_type"],  # type: ignore
                    input_summary=row["input_summary"],
                    output_summary=row["output_summary"],
                    reasoning=row["reasoning"],
                    confidence=row["confidence"],
                    model_backend=row["model_backend"],
                    latency_ms=row["latency_ms"],
                    tool_name=row["tool_name"],
                    tool_args_hash=row["tool_args_hash"],
                    sha256_anchor=row["sha256_anchor"],
                    timestamp=timestamp,
                )
                results.append(trace)

        return results

    def export_jsonl(self, session_id: str, out_path: Path) -> None:
        """Export traces for a specific session_id to a JSONL file."""
        traces = self.query(session_id=session_id, limit=100000)
        with open(out_path, "w") as f:
            for trace in sorted(traces, key=lambda t: (t.timestamp, t.step_index)):
                f.write(trace.model_dump_json() + "\n")
