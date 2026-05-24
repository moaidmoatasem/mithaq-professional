# packages/cherenkov/cve/matcher.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/cve.sqlite")

def match_package_version(package_name, version):
    """Find CVEs affecting a specific package version.
    
    Returns:
        List of {"cve": id, "summary": text, "cvss": score} dicts
    """
    if not DB_PATH.exists():
        return []
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Naive substring match on affected JSON
    # Production: implement proper CPE matching
    query_term = f"%{package_name}%"
    cur.execute(
        "SELECT id, summary, cvss FROM cves WHERE affected LIKE ? ORDER BY cvss DESC",
        (query_term,)
    )
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for cve_id, summary, cvss in rows:
        results.append({
            "cve": cve_id,
            "summary": summary[:200],  # Truncate for display
            "cvss": cvss
        })
    
    return results

if __name__ == "__main__":
    # Quick test
    matches = match_package_version("apache", "2.4.49")
    if matches:
        print(f"Found {len(matches)} CVEs:")
        for m in matches[:3]:
            print(f"  {m['cve']}: {m['summary']} (CVSS {m['cvss']})")
    else:
        print("No CVEs found (DB empty or no matches)")