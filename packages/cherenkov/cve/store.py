# packages/cherenkov/cve/store.py
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("data/cve.sqlite")

def init_db():
    """Initialize SQLite database with CVE schema."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cves (
        id TEXT PRIMARY KEY,
        summary TEXT,
        affected TEXT,
        cvss REAL,
        kev INTEGER,
        published_date TEXT
    )""")
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def upsert_from_staging(staging_path="data/cve_staging.json"):
    """Load staged CVE JSON and upsert into database."""
    staging_file = Path(staging_path)
    if not staging_file.exists():
        print(f"⚠️ Staging file not found: {staging_path}")
        return
    
    with open(staging_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    count = 0
    for item in data.get("CVE_Items", []):
        try:
            cve_id = item["cve"]["CVE_data_meta"]["ID"]
            desc_list = item["cve"]["description"]["description_data"]
            summary = desc_list[0]["value"][:2000] if desc_list else ""
            affected = json.dumps(item.get("configurations", {}))
            cvss = 0.0
            try:
                cvss = item["impact"]["baseMetricV3"]["cvssV3"]["baseScore"]
            except (KeyError, TypeError):
                pass
            kev = 0
            published = item["publishedDate"] if "publishedDate" in item else ""
            
            cur.execute(
                "INSERT OR REPLACE INTO cves (id, summary, affected, cvss, kev, published_date) VALUES (?, ?, ?, ?, ?, ?)",
                (cve_id, summary, affected, cvss, kev, published)
            )
            count += 1
        except (KeyError, IndexError) as e:
            pass  # Skip malformed entries
    
    conn.commit()
    conn.close()
    print(f"✅ Upserted {count} CVEs into {DB_PATH}")

if __name__ == "__main__":
    upsert_from_staging()