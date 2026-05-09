#!/usr/bin/env python3
"""
cherenkov - Simple Security Scanner
Minimal viable product - Actually works!
"""

import argparse
import asyncio
import concurrent.futures
import json
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

import requests

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class SimpleScanner(BaseScanner):
    """Basic security scanner that actually works"""

    def __init__(
        self,
        name: str = "SimpleScanner",
        description: str = "Basic security scanner",
        target_url: Optional[str] = None,
    ):
        super().__init__(name, description)
        self.target = target_url
        self.results = {}
        if target_url:
            self._setup_target(target_url)

    def _setup_target(self, target_url: str):
        parsed = urlparse(target_url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Unsupported scheme '{parsed.scheme}'. Only http/https are allowed.")
        if not parsed.netloc:
            raise ValueError("Invalid URL: missing hostname.")
        self.target = target_url
        self.results = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
        }

    def scan_security_headers(self, findings_list: List[Finding]):
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
                    # Update local state for legacy report formatting
                    vuln = {
                        "type": "Missing Security Header",
                        "severity": "Medium",
                        "header": header,
                        "description": f"Missing {header} ({purpose})",
                    }
                    self.results["vulnerabilities"].append(vuln)

                    # Update standardized Finding list
                    findings_list.append(
                        Finding(
                            title=f"Missing Security Header: {header}",
                            severity=Severity.MEDIUM,
                            description=f"Missing {header} ({purpose})",
                            cwe="CWE-693",  # Protection Mechanism Failure
                            remediation=f"Configure the server to emit the {header} header.",
                        )
                    )

                    print(f"  [!] MISSING: {header}")
                else:
                    print(f"  [✓] Found: {header}")

        except Exception as e:
            print(f"  [!] Error: {e}")

    def scan_http_methods(self, findings_list: List[Finding]):
        """Check for dangerous HTTP methods"""
        print("\n[*] Checking HTTP methods")

        dangerous_methods = ["PUT", "DELETE", "TRACE", "CONNECT"]

        def check_method(method):
            try:
                response = requests.request(method, self.target, timeout=5)
                return method, response, None
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.SSLError,
            ) as e:
                return method, None, e

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(dangerous_methods)) as executor:
            results = executor.map(check_method, dangerous_methods)

            for method, response, error in results:
                if error:
                    print(f"  [✓] {method} is blocked or unreachable")
                else:
                    if response.status_code not in [405, 501]:
                        vuln = {
                            "type": "Dangerous HTTP Method",
                            "severity": "High",
                            "method": method,
                            "description": f"{method} method is allowed",
                        }
                        self.results["vulnerabilities"].append(vuln)

                        findings_list.append(
                            Finding(
                                title=f"Dangerous HTTP Method Enabled: {method}",
                                severity=Severity.HIGH,
                                description=f"The {method} method is allowed (Status: {response.status_code})",
                                cwe="CWE-749",
                                remediation=f"Disable the {method} method in server configuration.",
                            )
                        )

                        print(f"  [!] {method} is ALLOWED (Status: {response.status_code})")
                    else:
                        print(f"  [✓] {method} is blocked")

    def scan_ssl_tls(self, findings_list: List[Finding]):
        """Check SSL/TLS configuration"""
        print("\n[*] Checking SSL/TLS")

        parsed = urlparse(self.target)
        if parsed.scheme != "https":
            vuln = {
                "type": "Insecure Protocol",
                "severity": "High",
                "description": "Site is not using HTTPS",
            }
            self.results["vulnerabilities"].append(vuln)

            findings_list.append(
                Finding(
                    title="Insecure Protocol (HTTP used)",
                    severity=Severity.HIGH,
                    description="Site is not using HTTPS",
                    cwe="CWE-319",
                    remediation="Enforce HTTPS across all traffic.",
                )
            )

            print("  [!] Site is using HTTP (insecure)")
        else:
            print("  [✓] Site is using HTTPS")

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

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Implement BaseScanner async scan method"""
        start_time = datetime.now()
        self._setup_target(target)

        findings: List[Finding] = []

        # In a fully asynchronous refactor, these would use aiohttp or httpx
        # For compatibility with legacy behavior, running them synchronously here
        # or via threadpool would be ideal, but for the MVP, direct call is fine.
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(None, self.scan_security_headers, findings)
        await loop.run_in_executor(None, self.scan_http_methods, findings)
        await loop.run_in_executor(None, self.scan_ssl_tls, findings)

        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )

    def run(self):
        """Run all scans"""
        print("=" * 70)
        print("🔍 cherenkov SECURITY SCANNER")
        print("=" * 70)

        findings = []
        self.scan_security_headers(findings)
        self.scan_http_methods(findings)
        self.scan_ssl_tls(findings)
        self.generate_report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="cherenkov - Simple Security Scanner")
    parser.add_argument("url", help="Target URL to scan (e.g., https://example.com)")

    args = parser.parse_args()

    scanner = SimpleScanner(args.url)
    scanner.run()
