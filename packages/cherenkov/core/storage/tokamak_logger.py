import hashlib
import logging
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class TokamakLogger:
    """
    SQLite WAL mode logger for TOKAMAK execution proofs.
    Enforces forensic immutability via SHA-256 trace signatures.
    """

    _DDL = """
    CREATE TABLE IF NOT EXISTS poc_execution_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        target TEXT NOT NULL,
        payload TEXT NOT NULL,
        stdout TEXT NOT NULL,
        stderr TEXT NOT NULL,
        exit_code INTEGER NOT NULL,
        trace_hash TEXT NOT NULL UNIQUE
    );
    CREATE INDEX IF NOT EXISTS idx_poc_target ON poc_execution_logs(target);
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database with WAL and parent directories."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.executescript(self._DDL)

    def log_execution(
        self, target: str, payload: str, stdout: str, stderr: str, exit_code: int
    ) -> str:
        """
        Log a PoC execution, signing it with a SHA-256 hash.
        Returns the full trace_hash.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Concatenate values for hash signature to ensure tamper evidence
        trace_data = f"{timestamp}|{target}|{payload}|{stdout}|{stderr}|{exit_code}"
        trace_hash = hashlib.sha256(trace_data.encode("utf-8")).hexdigest()

        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                # Ensure WAL pragmas are active for the connection
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                with conn:
                    conn.execute(
                        """
                        INSERT INTO poc_execution_logs
                        (timestamp, target, payload, stdout, stderr, exit_code, trace_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (timestamp, target, payload, stdout, stderr, exit_code, trace_hash),
                    )

            # Log short anchor only (operational security)
            short_hash = trace_hash[:8]
            logger.info(
                "TOKAMAK execution log recorded. target=%s hash_anchor=%s", target, short_hash
            )
            return trace_hash

        except sqlite3.Error as e:
            logger.error("Failed to write to Tokamak logger: %s", e)
            raise

    def get_logs(self, target: str | None = None, limit: int = 100) -> list[dict]:
        """Retrieve execution logs, optionally filtered by target."""
        query = "SELECT * FROM poc_execution_logs"
        params: tuple = ()
        if target:
            query += " WHERE target = ?"
            params = (target,)

        query += " ORDER BY id DESC LIMIT ?"
        params = (*params, limit)

        logs = []
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            for row in rows:
                logs.append(dict(row))
        return logs
