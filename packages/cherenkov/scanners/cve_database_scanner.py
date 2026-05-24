"""CVE Database Scanner — detects software version disclosure and maps to known CVEs offline."""

from __future__ import annotations

import re
import time

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

# Offline mapping of version patterns → CVE findings.
# Avoids any outbound calls beyond the target (MEISSNER invariant).
_CVE_SIGNATURES: list[tuple[re.Pattern[str], str, str, Severity, str, str]] = [
    (
        re.compile(r"Apache/([01]\.\d+|2\.[0-3])\.", re.IGNORECASE),
        "Apache httpd EOL version detected",
        "The Server header reveals an end-of-life Apache version that receives no security patches.",
        Severity.HIGH,
        "CWE-1104",
        "Upgrade to a supported Apache httpd release.",
    ),
    (
        re.compile(r"nginx/1\.(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18)\.", re.IGNORECASE),
        "Nginx version < 1.19 detected",
        "The Server header reveals an older nginx version. Versions below 1.19 contain known vulnerabilities.",
        Severity.MEDIUM,
        "CWE-1104",
        "Upgrade nginx to the latest stable release (1.26+).",
    ),
    (
        re.compile(r"PHP/([45]\.\d+\.\d+)", re.IGNORECASE),
        "PHP 4.x/5.x EOL version detected",
        "The X-Powered-By header reveals a PHP 4.x or 5.x version which is end-of-life.",
        Severity.CRITICAL,
        "CWE-1104",
        "Upgrade to PHP 8.1 or later immediately.",
    ),
    (
        re.compile(r"PHP/(7\.[01]\.\d+)", re.IGNORECASE),
        "PHP 7.0/7.1 EOL version detected",
        "The X-Powered-By header reveals PHP 7.0 or 7.1 which reached end-of-life.",
        Severity.HIGH,
        "CWE-1104",
        "Upgrade to PHP 8.1 or later.",
    ),
    (
        re.compile(r"OpenSSL/([01]\.\d+\.\d+)", re.IGNORECASE),
        "OpenSSL EOL version detected",
        "Server header reveals an OpenSSL 0.x or 1.0.x version with known critical CVEs.",
        Severity.CRITICAL,
        "CWE-1104",
        "Upgrade OpenSSL to 3.x.",
    ),
    (
        re.compile(r"Microsoft-IIS/([456789])\.", re.IGNORECASE),
        "IIS version 4–9 detected",
        "Server header reveals an older IIS version with known vulnerabilities.",
        Severity.HIGH,
        "CWE-1104",
        "Upgrade to IIS 10 and apply all security patches.",
    ),
    (
        re.compile(r"JBoss|Tomcat/([456789])\.", re.IGNORECASE),
        "Legacy Java application server detected",
        "Server header reveals an older JBoss/Tomcat version with known RCE vulnerabilities.",
        Severity.HIGH,
        "CWE-1104",
        "Upgrade to Tomcat 10+ and apply all security patches.",
    ),
]


class CVEDatabaseScanner(BaseScanner):
    """Detects software version disclosures and cross-references against known CVE patterns."""

    def __init__(self) -> None:
        super().__init__(
            name="cve_database",
            description="Detects server software versions and flags known-vulnerable versions",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: list[Finding] = []

        try:
            resp = await self._http_request(target, timeout)
        except Exception:
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=(time.monotonic() - start) * 1000,
                status="error",
            )

        # Collect banner strings from disclosure headers
        banner_headers = ["server", "x-powered-by", "x-aspnet-version", "via"]
        banners: list[str] = []
        for h in banner_headers:
            value = resp.headers.get(h)
            if value:
                banners.append(value)

        combined = " ".join(banners)

        for pattern, title, description, severity, cwe, remediation in _CVE_SIGNATURES:
            if pattern.search(combined):
                findings.append(
                    Finding(
                        title=title,
                        severity=severity,
                        description=description,
                        cwe=cwe,
                        remediation=remediation,
                    )
                )

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=(time.monotonic() - start) * 1000,
        )
