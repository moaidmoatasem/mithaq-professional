#!/usr/bin/env python3
"""
Enhanced cherenkov Scanner with more checks
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)

from cherenkov.core.base_scanner import Finding, ScanResult, Severity

from .header_scanner import SimpleScanner


class FullScanner(SimpleScanner):
    """Extended scanner with more vulnerability checks"""

    def __init__(
        self,
        name: str = "FullScanner",
        description: str = "Extended security scanner",
        target_url: Optional[str] = None,
    ):
        super().__init__(name=name, description=description, target_url=target_url)

    def scan_cors(self, findings_list: List[Finding]):
        """Check CORS configuration"""
        logger.info("[*] Checking CORS configuration")

        try:
            headers = {"Origin": "https://evil.com"}
            response = requests.get(self.target, headers=headers, timeout=10)

            if "Access-Control-Allow-Origin" in response.headers:
                origin = response.headers["Access-Control-Allow-Origin"]
                if origin == "*":
                    vuln = {
                        "type": "CORS Misconfiguration",
                        "severity": "High",
                        "description": "Access-Control-Allow-Origin is set to wildcard (*)",
                    }
                    self.results["vulnerabilities"].append(vuln)

                    findings_list.append(
                        Finding(
                            title="CORS Misconfiguration",
                            severity=Severity.HIGH,
                            description="Access-Control-Allow-Origin is set to wildcard (*)",
                            cwe="CWE-346",
                            remediation="Restrict CORS to trusted origins only.",
                        )
                    )
                    logger.warning("  [!] CORS allows ANY origin (*)")
                else:
                    logger.info("  [✓] CORS configured: %s", origin)
            else:
                logger.info("  [✓] CORS not enabled")
        except Exception as e:
            logger.error("  [!] Error: %s", e)

    def scan_cookies(self, findings_list: List[Finding]):
        """Check cookie security"""
        logger.info("[*] Checking cookie security")

        try:
            response = requests.get(self.target, timeout=10)

            if "Set-Cookie" in response.headers:
                cookies = response.headers["Set-Cookie"]

                if "Secure" not in cookies:
                    vuln = {
                        "type": "Insecure Cookie",
                        "severity": "Medium",
                        "description": "Cookies missing Secure flag",
                    }
                    self.results["vulnerabilities"].append(vuln)
                    findings_list.append(
                        Finding(
                            title="Insecure Cookie (Missing Secure Flag)",
                            severity=Severity.MEDIUM,
                            description="Cookies are missing the Secure flag.",
                            cwe="CWE-614",
                            remediation="Add the Secure flag to cookies.",
                        )
                    )
                    logger.warning("  [!] Cookies missing Secure flag")

                if "HttpOnly" not in cookies:
                    vuln = {
                        "type": "Insecure Cookie",
                        "severity": "Medium",
                        "description": "Cookies missing HttpOnly flag",
                    }
                    self.results["vulnerabilities"].append(vuln)
                    findings_list.append(
                        Finding(
                            title="Insecure Cookie (Missing HttpOnly Flag)",
                            severity=Severity.MEDIUM,
                            description="Cookies are missing the HttpOnly flag.",
                            cwe="CWE-1004",
                            remediation="Add the HttpOnly flag to cookies.",
                        )
                    )
                    logger.warning("  [!] Cookies missing HttpOnly flag")

                if "SameSite" not in cookies:
                    logger.warning("  [!] Cookies missing SameSite attribute")
            else:
                logger.info("  [✓] No cookies set")
        except Exception as e:
            logger.error("  [!] Error: %s", e)

    def scan_server_info(self, findings_list: List[Finding]):
        """Check for information disclosure"""
        logger.info("[*] Checking for information disclosure")

        try:
            response = requests.get(self.target, timeout=10)

            if "Server" in response.headers:
                server = response.headers["Server"]
                vuln = {
                    "type": "Information Disclosure",
                    "severity": "Low",
                    "description": f"Server header disclosed: {server}",
                }
                self.results["vulnerabilities"].append(vuln)
                findings_list.append(
                    Finding(
                        title="Information Disclosure (Server Header)",
                        severity=Severity.LOW,
                        description=f"Server header disclosed: {server}",
                        cwe="CWE-200",
                        remediation="Remove or obfuscate the Server header.",
                    )
                )
                logger.warning("  [!] Server header exposed: %s", server)
            else:
                logger.info("  [✓] Server header hidden")

            if "X-Powered-By" in response.headers:
                powered = response.headers["X-Powered-By"]
                vuln = {
                    "type": "Information Disclosure",
                    "severity": "Low",
                    "description": f"X-Powered-By header disclosed: {powered}",
                }
                self.results["vulnerabilities"].append(vuln)
                findings_list.append(
                    Finding(
                        title="Information Disclosure (X-Powered-By Header)",
                        severity=Severity.LOW,
                        description=f"X-Powered-By header disclosed: {powered}",
                        cwe="CWE-200",
                        remediation="Remove or obfuscate the X-Powered-By header.",
                    )
                )
                logger.warning("  [!] X-Powered-By exposed: %s", powered)
            else:
                logger.info("  [✓] X-Powered-By header hidden")
        except Exception as e:
            logger.error("  [!] Error: %s", e)

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Implement BaseScanner async scan method"""
        start_time = datetime.now()
        self._setup_target(target)

        findings: List[Finding] = []

        loop = asyncio.get_event_loop()

        # Superclass checks
        await loop.run_in_executor(None, self.scan_security_headers, findings)
        await loop.run_in_executor(None, self.scan_http_methods, findings)
        await loop.run_in_executor(None, self.scan_ssl_tls, findings)

        # Own checks
        await loop.run_in_executor(None, self.scan_cors, findings)
        await loop.run_in_executor(None, self.scan_cookies, findings)
        await loop.run_in_executor(None, self.scan_server_info, findings)

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
        """Run all scans including new ones"""
        logger.info("=" * 70)
        logger.info("🔍 cherenkov FULL SECURITY SCANNER")
        logger.info("=" * 70)

        findings = []
        self.scan_security_headers(findings)
        self.scan_http_methods(findings)
        self.scan_ssl_tls(findings)
        self.scan_cors(findings)
        self.scan_cookies(findings)
        self.scan_server_info(findings)
        self.generate_report()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        scanner = FullScanner(sys.argv[1])
        scanner.run()
