#!/usr/bin/env python3
"""
cherenkov - Simple Security Scanner
Minimal viable product - Actually works!
"""

import httpx
import argparse
import concurrent.futures
from urllib.parse import urlparse
import json
from datetime import datetime
import asyncio
from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity


class HeaderScanner(BaseScanner):
    """Basic security scanner that actually works"""

    def __init__(
        self,
        name: str = "HeaderScanner",
        description: str = "Basic security header scanner",
    ):
        super().__init__(name, description)
        self.results = {
            "vulnerabilities": [],
        }

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        start_time = datetime.now()

        parsed = urlparse(target)
        if parsed.scheme not in ("http", "https"):
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=0,
                status="failed: invalid scheme",
            )
        if not parsed.netloc:
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=0,
                status="failed: missing hostname",
            )

        self.results = {
            "vulnerabilities": [],
        }

        await self.scan_security_headers()
        await self.scan_http_methods()
        self.scan_ssl_tls()

        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        findings = []
        for vuln in self.results["vulnerabilities"]:
            severity = Severity.MEDIUM
            if vuln["severity"] == "High":
                severity = Severity.HIGH

            findings.append(
                Finding(
                    title=vuln["type"],
                    severity=severity,
                    description=vuln.get("description", ""),
                    cwe="",
                    remediation="",
                )
            )

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )

    async def scan_security_headers(self):
        """Check for missing security headers"""
        try:
            response = await self._http_request(self.target, timeout=10)
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
                # case insensitive check
                header_lower = header.lower()
                found = any(k.lower() == header_lower for k in headers.keys())

                if not found:
                    vuln = {
                        "type": "Missing Security Header",
                        "severity": "Medium",
                        "header": header,
                        "description": f"Missing {header} ({purpose})",
                    }
                    self.results["vulnerabilities"].append(vuln)

        except Exception as e:
            pass

    async def scan_http_methods(self):
        """Check for dangerous HTTP methods"""
        dangerous_methods = ["PUT", "DELETE", "TRACE", "CONNECT"]

        async def check_method(method):
            try:
                async with httpx.AsyncClient(timeout=5, verify=True) as client:
                    response = await client.request(method, self.target)
                    return method, response, None
            except Exception as e:
                return method, None, e

        tasks = [check_method(method) for method in dangerous_methods]
        results = await asyncio.gather(*tasks)

        for method, response, error in results:
            if not error:
                if response.status_code not in [405, 501, 400, 403, 404]:
                    vuln = {
                        "type": "Dangerous HTTP Method",
                        "severity": "High",
                        "method": method,
                        "description": f"{method} method is allowed (Status: {response.status_code})",
                    }
                    self.results["vulnerabilities"].append(vuln)

    def scan_ssl_tls(self):
        """Check SSL/TLS configuration"""
        parsed = urlparse(self.target)
        if parsed.scheme != "https":
            vuln = {
                "type": "Insecure Protocol",
                "severity": "High",
                "description": "Site is not using HTTPS",
            }
            self.results["vulnerabilities"].append(vuln)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="cherenkov - Simple Security Scanner")
    parser.add_argument("url", help="Target URL to scan (e.g., https://example.com)")

    args = parser.parse_args()

    scanner = HeaderScanner()
    result = asyncio.run(scanner.scan(args.url))
    print(result.json(indent=2))
