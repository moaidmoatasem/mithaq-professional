import logging
import sqlite3
from pathlib import Path

from cherenkov.core.schemas.reasoning_trace import ReasoningTrace

logger = logging.getLogger(__name__)


class ReasoningStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reasoning_traces (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        step_type TEXT NOT NULL,
                        input_summary TEXT NOT NULL,
                        output_summary TEXT NOT NULL,
                        reasoning TEXT NOT NULL,
                        model_backend TEXT NOT NULL,
                        latency_ms REAL NOT NULL,
                        confidence REAL,
                        sha256_anchor TEXT NOT NULL,
                        timestamp DATETIME NOT NULL
                    )
                    """
                )
        except Exception as e:
            logger.error("Failed to init ReasoningStore db: %s", e)

    def record(self, trace: ReasoningTrace):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO reasoning_traces (
                        step_type, input_summary, output_summary, reasoning,
                        model_backend, latency_ms, confidence, sha256_anchor, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        trace.step_type,
                        trace.input_summary,
                        trace.output_summary,
                        trace.reasoning,
                        trace.model_backend,
                        trace.latency_ms,
                        trace.confidence,
                        trace.sha256_anchor,
                        trace.timestamp.isoformat(),
                    ),
                )
        except Exception as e:
            logger.error("Failed to record reasoning trace: %s", e)
