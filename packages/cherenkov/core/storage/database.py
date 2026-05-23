import hashlib
import sqlite3

class FindingsLogger:
    def __init__(self, db_path):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path, isolation_level=None, uri=True)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_findings (
                sha256_hash TEXT PRIMARY KEY,
                poc TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def finding_exists(self, sha256_hash):
        conn = sqlite3.connect(self.db_path, isolation_level=None, uri=True)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM security_findings WHERE sha256_hash = ?', (sha256_hash,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def generate_poc(self, finding):
        # Placeholder for PoC generation logic
        return f"PoC for {finding}"

    def log_finding(self, finding):
        sha256_hash = hashlib.sha256(finding.encode()).hexdigest()
        if self.finding_exists(sha256_hash):
            return f"Finding already logged: {sha256_hash}"
        poc = self.generate_poc(finding)
        conn = sqlite3.connect(self.db_path, isolation_level=None, uri=True)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO security_findings (sha256_hash, poc) VALUES (?, ?)', (sha256_hash, poc))
        conn.commit()
        conn.close()
        return f"Finding logged: {sha256_hash}"