import hashlib
import sqlite3

class SQLiteWALLogger:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, isolation_level='EXCLUSIVE')
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cherenkov_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace TEXT NOT NULL,
                sha256 TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def log_trace(self, trace):
        if not isinstance(trace, str):
            raise ValueError("Trace must be a string")
        
        sha256 = hashlib.sha256(trace.encode()).hexdigest()
        
        self.cursor.execute('''
            INSERT INTO cherenkov_traces (trace, sha256) VALUES (?, ?)
        ''', (trace, sha256))
        self.conn.commit()

    def get_all_traces(self):
        self.cursor.execute('SELECT * FROM cherenkov_traces')
        return self.cursor.fetchall()