# packages/cherenkov/cve/__init__.py
"""
CVE Intelligence Pipeline — Air-gapped NVD Integration

Modules:
  - ingest.py: Download and verify NVD JSON (SHA256 + GPG)
  - store.py: Persist CVE records to SQLite WAL
  - matcher.py: Query CVEs by package name/version
  - scanner.py: BaseScanner integration for finding attachment
"""

from .scanner import CVEScanner

__all__ = ["CVEScanner"]
