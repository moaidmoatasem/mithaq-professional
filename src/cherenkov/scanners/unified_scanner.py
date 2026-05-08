#!/usr/bin/env python3
"""
Unified Security Scanner
Runs all refined scanners on a target
"""

import sys

sys.path.insert(0, "cherenkov/scanners/refined")

import json
from datetime import datetime

from csrf_scanner import scan_csrf
from open_redirect_scanner import scan_open_redirect
from xss_scanner import scan_xss

from ..header_scanner import SimpleScanner


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
        print("\n" + "=" * 70)
        print("🔍 UNIFIED SECURITY SCANNER")
        print("=" * 70)
        print(f"Target: {self.target}\n")

        # 1. Header Scanner
        print("1️⃣ Running Security Header Scan...")
        header_scanner = SimpleScanner(self.target)
        header_scanner.scan_security_headers()
        header_scanner.scan_http_methods()
        header_scanner.scan_ssl_tls()
        self.results["scans"]["headers"] = header_scanner.results

        # 2. XSS Scanner
        print("\n2️⃣ Running XSS Scan...")
        xss_results = scan_xss(self.target)
        self.results["scans"]["xss"] = xss_results

        # 3. CSRF Scanner
        print("\n3️⃣ Running CSRF Scan...")
        csrf_results = scan_csrf(self.target)
        self.results["scans"]["csrf"] = csrf_results

        # 4. Open Redirect Scanner
        print("\n4️⃣ Running Open Redirect Scan...")
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
        print("\n" + "=" * 70)
        print("📊 SCAN SUMMARY")
        print("=" * 70)
        print(f"Target: {self.target}")
        print(f"Total Vulnerabilities: {self.results['total_vulnerabilities']}")
        print("\nBy Scanner:")
        print(f"  • Headers: {len(self.results['scans']['headers'].get('vulnerabilities', []))}")
        print(f"  • XSS: {self.results['scans']['xss'].get('count', 0)}")
        print(f"  • CSRF: {self.results['scans']['csrf'].get('count', 0)}")
        print(f"  • Open Redirect: {self.results['scans']['open_redirect'].get('count', 0)}")

    def save_report(self, filename=None):
        """Save scan report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unified_scan_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Report saved: {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python unified_scanner.py <target_url>")
        sys.exit(1)

    scanner = UnifiedSecurityScanner(sys.argv[1])
    scanner.run_all_scans()
    scanner.save_report()
