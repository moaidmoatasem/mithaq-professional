<<<<<<< HEAD
import os
import hashlib
from datetime import datetime
import sqlite3

class SecurityFindingLogger:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, journal_mode='WAL')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_findings (
                trace_id TEXT PRIMARY KEY,
                timestamp TEXT,
                finding TEXT
=======
import sqlite3
import hashlib

class SQLiteWALLogger:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, isolation_level=None)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.cursor = self.conn.cursor()
        self.setup_table()

    def setup_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finding TEXT NOT NULL,
                trace TEXT NOT NULL
>>>>>>> origin/main
            )
        ''')
        self.conn.commit()

    def log_finding(self, finding):
<<<<<<< HEAD
        timestamp = datetime.now().isoformat()
        trace_id = hashlib.sha256(f"{timestamp}{finding}".encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO security_findings (trace_id, timestamp, finding) VALUES (?, ?, ?)',
                       (trace_id, timestamp, finding))
        self.conn.commit()

    def shred_receipt(self, receipt_path):
        os.remove(receipt_path)

# Example usage:
if __name__ == "__main__":
    logger = SecurityFindingLogger('security_findings.db')
    logger.log_finding("Potential security breach detected")
    logger.shred_receipt('path_to_shred')
=======
        trace = self.hash_finding(finding)
        self.cursor.execute('INSERT INTO security_findings (finding, trace) VALUES (?, ?)', (finding, trace))
        self.conn.commit()

    def hash_finding(self, finding):
        return hashlib.sha256(finding.encode()).hexdigest()

    def close(self):
        self.conn.close()
>>>>>>> origin/main
