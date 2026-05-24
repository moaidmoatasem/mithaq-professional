#!/usr/bin/env python3
"""
Unified Security Scanner
Runs all refined scanners on a target
"""

import json
import logging
import sys
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

sys.path.insert(0, "cherenkov/scanners/refined")  # noqa: E402
from csrf_scanner import scan_csrf  # noqa: E402
from open_redirect_scanner import scan_open_redirect  # noqa: E402
from xss_scanner import scan_xss  # noqa: E402

from ..header_scanner import SimpleScanner  # noqa: E402


class UnifiedSecurityScanner:
    """Run all security scans on a target"""

    def __init__(self, target_url: str):
        self.target = target_url
        self.results = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "scans": {},
            "total_vulnerabilities": 0,
        }

    def run_all_scans(self):
        """Execute all scanners"""
        logger.info("=" * 70)
        logger.info("UNIFIED SECURITY SCANNER")
        logger.info("=" * 70)
        logger.info("Target: %s", self.target)

        # 1. Header Scanner
        logger.info("Running Security Header Scan...")
        header_scanner = SimpleScanner(self.target)
        header_scanner.scan_security_headers()
        header_scanner.scan_http_methods()
        header_scanner.scan_ssl_tls()
        self.results["scans"]["headers"] = header_scanner.results

        # 2. XSS Scanner
        logger.info("Running XSS Scan...")
        xss_results = scan_xss(self.target)
        self.results["scans"]["xss"] = xss_results

        # 3. CSRF Scanner
        logger.info("Running CSRF Scan...")
        csrf_results = scan_csrf(self.target)
        self.results["scans"]["csrf"] = csrf_results

        # 4. Open Redirect Scanner
        logger.info("Running Open Redirect Scan...")
        redirect_results = scan_open_redirect(self.target)
        self.results["scans"]["open_redirect"] = redirect_results

        # Calculate totals
        self.results["total_vulnerabilities"] = (
            len(self.results["scans"]["headers"].get("vulnerabilities", []))
            + xss_results.get("count", 0)
            + csrf_results.get("count", 0)
            + redirect_results.get("count", 0)
        )

        self._print_summary()
        return self.results

    def _print_summary(self):
        """Print scan summary"""
        logger.info("=" * 70)
        logger.info("SCAN SUMMARY")
        logger.info("=" * 70)
        logger.info("Target: %s", self.target)
        logger.info("Total Vulnerabilities: %s", self.results["total_vulnerabilities"])
        logger.info("By Scanner:")
        logger.info(
            "  - Headers: %s", len(self.results["scans"]["headers"].get("vulnerabilities", []))
        )
        logger.info("  - XSS: %s", self.results["scans"]["xss"].get("count", 0))
        logger.info("  - CSRF: %s", self.results["scans"]["csrf"].get("count", 0))
        logger.info("  - Open Redirect: %s", self.results["scans"]["open_redirect"].get("count", 0))

    def save_report(self, filename: Optional[str] = None) -> None:
        """Save scan report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unified_scan_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info("Report saved: %s", filename)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python unified_scanner.py <target_url>")
        sys.exit(1)

    scanner = UnifiedSecurityScanner(sys.argv[1])
    scanner.run_all_scans()
    scanner.save_report()
