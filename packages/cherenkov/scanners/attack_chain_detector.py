"""Attack Chain Detector — identifies co-occurring vulnerabilities that form exploitable chains."""

from __future__ import annotations

import time
from urllib.parse import urlparse

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

# Pairs of response indicators that together form a dangerous attack chain.
# Each entry: (probe_path, indicator_fn, chain_title, chain_description, severity, cwe, remediation)
_CHAIN_PROBES: list[tuple[str, str, Severity, str, str]] = [
    (
        "/.git/HEAD",
        "Git repository exposed — combine with directory traversal for full source disclosure",
        Severity.CRITICAL,
        "CWE-538",
        "Block web access to .git/ in server config (e.g. 'deny all' for /.git location).",
    ),
    (
        "/phpinfo.php",
        "phpinfo() exposed — reveals config chain: PHP version + loaded extensions + env vars",
        Severity.HIGH,
        "CWE-200",
        "Remove phpinfo.php from production. Gate diagnostic pages behind auth.",
    ),
    (
        "/.env",
        ".env exposed — secrets chain: DB credentials + API keys + JWT secrets",
        Severity.CRITICAL,
        "CWE-312",
        "Block access to .env at the web server level. Rotate all exposed secrets immediately.",
    ),
    (
        "/actuator/heapdump",
        "Spring Boot heap dump exposed — memory chain: credentials + tokens extracted from heap",
        Severity.CRITICAL,
        "CWE-200",
        "Secure /actuator endpoints behind authentication and remove heapdump in production.",
    ),
    (
        "/actuator/env",
        "Spring Boot /actuator/env exposed — config chain: all env vars including secrets",
        Severity.CRITICAL,
        "CWE-200",
        "Restrict /actuator/env access to localhost only or disable in production.",
    ),
    (
        "/v2/_catalog",
        "Docker Registry catalog exposed — image chain: enumerate all stored container images",
        Severity.HIGH,
        "CWE-200",
        "Enable Docker Registry authentication and restrict network access.",
    ),
    (
        "/console",
        "Web console exposed — RCE chain: interactive shell without authentication",
        Severity.CRITICAL,
        "CWE-78",
        "Disable the web console in production or gate it behind strong authentication and IP allowlisting.",
    ),
    (
        "/solr/admin/info/system",
        "Solr admin UI exposed — data chain: full index access and potential RCE via dataImport",
        Severity.HIGH,
        "CWE-284",
        "Restrict Solr admin to localhost or a VPN-only network segment.",
    ),
    (
        "/manager/html",
        "Tomcat Manager exposed — deployment chain: upload WAR for RCE",
        Severity.CRITICAL,
        "CWE-284",
        "Remove Tomcat Manager from production or restrict to localhost with strong credentials.",
    ),
]


class AttackChainDetector(BaseScanner):
    """Detects co-occurring vulnerabilities that can be chained into critical exploits."""

    def __init__(self) -> None:
        super().__init__(
            name="attack_chain_detector",
            description=(
                "Probes for high-value targets that form exploitable attack chains "
                "(RCE, full data disclosure, credential theft)"
            ),
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: list[Finding] = []

        parsed = urlparse(target)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for path, description, severity, cwe, remediation in _CHAIN_PROBES:
            url = base.rstrip("/") + path
            try:
                resp = await self._http_request(url, timeout)
                if resp.status_code == 200:
                    findings.append(
                        Finding(
                            title=f"Attack-chain pivot: {path} accessible",
                            severity=severity,
                            description=description,
                            cwe=cwe,
                            remediation=remediation,
                        )
                    )
            except Exception:
                pass

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=(time.monotonic() - start) * 1000,
        )
