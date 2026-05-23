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
            )
        ''')
        self.conn.commit()

    def log_finding(self, finding):
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