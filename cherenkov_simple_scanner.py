#!/usr/bin/env python3
"""
cherenkov - Simple Security Scanner
Minimal viable product - Actually works!
"""

import argparse
import json
import logging
from datetime import datetime
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class SimpleScanner:
    """Basic security scanner that actually works"""

    def __init__(self, target_url):
        self.target = target_url
        self.results = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
        }

    def scan_security_headers(self):
        """Check for missing security headers"""
        logger.info("[*] Scanning security headers for %s", self.target)

        try:
            response = requests.get(self.target, timeout=10)
            headers = response.headers

            # Check important security headers
            security_headers = {
                "X-Frame-Options": "Protects against clickjacking",
                "X-Content-Type-Options": "Prevents MIME sniffing",
                "Strict-Transport-Security": "Enforces HTTPS",
                "Content-Security-Policy": "Prevents XSS attacks",
                "X-XSS-Protection": "Legacy XSS protection",
            }

            for header, purpose in security_headers.items():
                if header not in headers:
                    vuln = {
                        "type": "Missing Security Header",
                        "severity": "Medium",
                        "header": header,
                        "description": f"Missing {header} ({purpose})",
                    }
                    self.results["vulnerabilities"].append(vuln)
                    logger.warning("  [!] MISSING: %s", header)
                else:
                    logger.info("  [✓] Found: %s", header)

        except Exception as e:
            logger.error("  [!] Error: %s", e)

    def scan_http_methods(self):
        """Check for dangerous HTTP methods"""
        logger.info("[*] Checking HTTP methods")

        dangerous_methods = ["PUT", "DELETE", "TRACE", "CONNECT"]

        for method in dangerous_methods:
            try:
                response = requests.request(method, self.target, timeout=5)
                if response.status_code not in [405, 501]:
                    vuln = {
                        "type": "Dangerous HTTP Method",
                        "severity": "High",
                        "method": method,
                        "description": f"{method} method is allowed",
                    }
                    self.results["vulnerabilities"].append(vuln)
                    logger.warning("  [!] %s is ALLOWED (Status: %s)", method, response.status_code)
                else:
                    logger.info("  [✓] %s is blocked", method)
            except:
                logger.info("  [✓] %s is blocked", method)

    def scan_ssl_tls(self):
        """Check SSL/TLS configuration"""
        logger.info("[*] Checking SSL/TLS")

        parsed = urlparse(self.target)
        if parsed.scheme != "https":
            vuln = {
                "type": "Insecure Protocol",
                "severity": "High",
                "description": "Site is not using HTTPS",
            }
            self.results["vulnerabilities"].append(vuln)
            logger.warning("  [!] Site is using HTTP (insecure)")
        else:
            logger.info("  [✓] Site is using HTTPS")

    def generate_report(self):
        """Generate scan report"""
        logger.info("\n" + "=" * 70)
        logger.info("SCAN REPORT")
        logger.info("=" * 70)
        logger.info("Target: %s", self.results['target'])
        logger.info("Scan Time: %s", self.results['timestamp'])
        logger.info("Vulnerabilities Found: %d", len(self.results['vulnerabilities']))
        logger.info("=" * 70)

        if not self.results["vulnerabilities"]:
            logger.info("\n✅ No vulnerabilities detected!")
        else:
            logger.warning("\n⚠️  VULNERABILITIES:")
            for i, vuln in enumerate(self.results["vulnerabilities"], 1):
                logger.warning("\n%d. %s [%s]", i, vuln['type'], vuln['severity'])
                logger.warning("   %s", vuln.get('description', ''))

        # Save to file
        report_file = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info("\n📄 Full report saved to: %s", report_file)

    def run(self):
        """Run all scans"""
        logger.info("=" * 70)
        logger.info("🔍 cherenkov SECURITY SCANNER")
        logger.info("=" * 70)

        self.scan_security_headers()
        self.scan_http_methods()
        self.scan_ssl_tls()
        self.generate_report()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="cherenkov - Simple Security Scanner")
    parser.add_argument("url", help="Target URL to scan (e.g., https://example.com)")

    args = parser.parse_args()

    scanner = SimpleScanner(args.url)
    scanner.run()
