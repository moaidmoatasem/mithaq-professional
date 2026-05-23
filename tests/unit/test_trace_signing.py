import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cherenkov.core.aggregator import ScanAggregator
from cherenkov.core.base_scanner import Finding, ScanResult, Severity
from cherenkov.core.storage.database import _DB_PATH, get_trace, init_db


class TestTraceSigning(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for the tests
        self.fd, self.path = tempfile.mkstemp()
        os.close(self.fd)
        self.db_path = Path(self.path)
        init_db(self.db_path)

        # Patch the default DB_PATH to use our temp db
        self.db_patcher = patch("cherenkov.core.storage.database._DB_PATH", self.db_path)
        self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()
        if self.db_path.exists():
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_aggregator_generates_trace_hash(self):
        """Verify aggregator signs scan results with a valid 64-char SHA-256 trace_hash."""
        f = Finding(
            title="SQL Injection",
            severity=Severity.HIGH,
            description="SQL Injection in parameter id",
            cwe="CWE-89",
            remediation="Use parameterized queries",
        )
        res = ScanResult(
            target="http://example.com",
            scanner_name="sqli_scanner",
            findings=[f],
            duration_ms=100.0,
        )

        merged = ScanAggregator.aggregate([res])
        self.assertIsNotNone(merged.trace_hash)
        self.assertEqual(len(merged.trace_hash), 64)

    def test_aggregator_collects_trace_hashes(self):
        """Verify aggregator gathers and deduplicates individual trace hashes."""
        f1 = Finding(
            title="SQL Injection",
            severity=Severity.HIGH,
            description="SQL Injection",
            cwe="CWE-89",
            remediation="Remediation",
            trace_hash="finding_hash_1",
        )
        f2 = Finding(
            title="XSS",
            severity=Severity.MEDIUM,
            description="Reflected XSS",
            cwe="CWE-79",
            remediation="Remediation",
            trace_hash="finding_hash_2",
        )

        res1 = ScanResult(
            target="http://example.com",
            scanner_name="sqli_scanner",
            findings=[f1],
            duration_ms=50.0,
            trace_hash="res_hash_1",
            trace_hashes=["shared_hash"],
        )
        res2 = ScanResult(
            target="http://example.com",
            scanner_name="xss_scanner",
            findings=[f2],
            duration_ms=50.0,
            trace_hash="res_hash_2",
            trace_hashes=["shared_hash", "another_hash"],
        )

        merged = ScanAggregator.aggregate([res1, res2])
        expected_hashes = sorted(
            [
                "finding_hash_1",
                "finding_hash_2",
                "res_hash_1",
                "res_hash_2",
                "shared_hash",
                "another_hash",
            ]
        )
        self.assertEqual(merged.trace_hashes, expected_hashes)

    def test_aggregator_persists_trace_in_wal_db(self):
        """Verify that aggregator persists the signed trace in the SQLite WAL database."""
        f = Finding(
            title="SSRF",
            severity=Severity.HIGH,
            description="SSRF vulnerability",
            cwe="CWE-918",
            remediation="Validate input",
        )
        res = ScanResult(
            target="http://example.com",
            scanner_name="ssrf_scanner",
            findings=[f],
            duration_ms=200.0,
        )

        merged = ScanAggregator.aggregate([res])
        trace_hash = merged.trace_hash

        # Retrieve all trace records to find our persisted aggregator trace
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM cherenkov_traces WHERE trace_hash = ?", (trace_hash,)
        ).fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row["exploit_command"], "scan_aggregation")
        self.assertEqual(row["trace_hash"], trace_hash)
