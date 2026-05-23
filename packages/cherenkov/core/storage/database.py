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
            )
        ''')
        self.conn.commit()

    def log_finding(self, finding):
        trace = self.hash_finding(finding)
        self.cursor.execute('INSERT INTO security_findings (finding, trace) VALUES (?, ?)', (finding, trace))
        self.conn.commit()

    def hash_finding(self, finding):
        return hashlib.sha256(finding.encode()).hexdigest()

    def close(self):
        self.conn.close()