#!/usr/bin/env python3
"""
DAQIQ - Simple Security Scanner
Minimal viable product - Actually works!
"""

import requests
import argparse
from urllib.parse import urlparse
import json
from datetime import datetime


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
        print(f"\n[*] Scanning security headers for {self.target}")

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
                    print(f"  [!] MISSING: {header}")
                else:
                    print(f"  [✓] Found: {header}")

        except Exception as e:
            print(f"  [!] Error: {e}")

    def scan_http_methods(self):
        """Check for dangerous HTTP methods"""
        print(f"\n[*] Checking HTTP methods")

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
                    print(f"  [!] {method} is ALLOWED (Status: {response.status_code})")
                else:
                    print(f"  [✓] {method} is blocked")
            except:
                print(f"  [✓] {method} is blocked")

    def scan_ssl_tls(self):
        """Check SSL/TLS configuration"""
        print(f"\n[*] Checking SSL/TLS")

        parsed = urlparse(self.target)
        if parsed.scheme != "https":
            vuln = {
                "type": "Insecure Protocol",
                "severity": "High",
                "description": "Site is not using HTTPS",
            }
            self.results["vulnerabilities"].append(vuln)
            print(f"  [!] Site is using HTTP (insecure)")
        else:
            print(f"  [✓] Site is using HTTPS")

    def generate_report(self):
        """Generate scan report"""
        print("\n" + "=" * 70)
        print("SCAN REPORT")
        print("=" * 70)
        print(f"Target: {self.results['target']}")
        print(f"Scan Time: {self.results['timestamp']}")
        print(f"Vulnerabilities Found: {len(self.results['vulnerabilities'])}")
        print("=" * 70)

        if not self.results["vulnerabilities"]:
            print("\n✅ No vulnerabilities detected!")
        else:
            print("\n⚠️  VULNERABILITIES:")
            for i, vuln in enumerate(self.results["vulnerabilities"], 1):
                print(f"\n{i}. {vuln['type']} [{vuln['severity']}]")
                print(f"   {vuln.get('description', '')}")

        # Save to file
        report_file = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Full report saved to: {report_file}")

    def run(self):
        """Run all scans"""
        print("=" * 70)
        print("🔍 DAQIQ SECURITY SCANNER")
        print("=" * 70)

        self.scan_security_headers()
        self.scan_http_methods()
        self.scan_ssl_tls()
        self.generate_report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAQIQ - Simple Security Scanner")
    parser.add_argument("url", help="Target URL to scan (e.g., https://example.com)")

    args = parser.parse_args()

    scanner = SimpleScanner(args.url)
    scanner.run()
