import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ReasoningTrace(BaseModel):
    session_id: str
    trace_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    agent_id: str
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    anchor: Optional[str] = None

    def compute_anchor(self) -> str:
        content = f"{self.session_id}:{self.trace_id}:{self.timestamp}:{self.agent_id}:{self.action}:{json.dumps(self.details, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()


class ReasoningStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.traces: List[ReasoningTrace] = []
        self._load()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    anchor TEXT
                )
            """)
            conn.commit()

    def _load(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM traces ORDER BY timestamp ASC")
            for row in cursor:
                trace = ReasoningTrace(
                    session_id=row["session_id"],
                    trace_id=row["trace_id"],
                    timestamp=row["timestamp"],
                    agent_id=row["agent_id"],
                    action=row["action"],
                    details=json.loads(row["details"]),
                    anchor=row["anchor"],
                )
                self.traces.append(trace)

    def _save(self, trace: ReasoningTrace):
        if not trace.anchor:
            trace.anchor = trace.compute_anchor()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO traces (trace_id, session_id, timestamp, agent_id, action, details, anchor) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    trace.trace_id,
                    trace.session_id,
                    trace.timestamp,
                    trace.agent_id,
                    trace.action,
                    json.dumps(trace.details),
                    trace.anchor,
                ),
            )
            conn.commit()

    def append_trace(self, trace: ReasoningTrace):
        self.traces.append(trace)
        self._save(trace)

    def query(self) -> List[ReasoningTrace]:
        return self.traces

    def show(self, session_id: str):
        traces = self.query()
        for idx, t in enumerate(traces):
            if t.session_id == session_id:
                anchor_display = t.anchor[:8] if t.anchor else "None"
                print(
                    f"Step {idx:02d} | trace_id={t.trace_id} | anchor={anchor_display}"
                )

    def verify(self, session_id: str):
        traces = [t for t in self.query() if t.session_id == session_id]
        failed_count = 0
        total_steps = len(traces)

        for idx, t in enumerate(traces):
            recomputed = t.compute_anchor()
            if t.anchor == recomputed:
                anchor_display = t.anchor if t.anchor else "None"
                print(
                    f"[PASS] Step {idx:02d} | trace_id={t.trace_id} | anchor={anchor_display}..."
                )
            else:
                failed_count += 1
                stored_disp = t.anchor if t.anchor else "None"
                recomp_disp = recomputed
                print(
                    f"[FAIL] Step {idx:02d} | trace_id={t.trace_id} | stored={stored_disp}... recomputed={recomp_disp}..."
                )

        if failed_count > 0:
            print(
                f"Tamper detected: {failed_count} of {total_steps} steps failed anchor verification."
            )
        else:
            print(
                f"Verification passed: 0 of {total_steps} steps failed anchor verification."
            )
