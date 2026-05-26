"""CVE Database Scanner - Local-Only Implementation (MEISSNER air-gapped)"""

import json
import logging
import pathlib
import re
import time
from typing import Dict, List
from urllib.parse import urlparse

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger(__name__)

# Fallback default CVE list if local cves.json is missing or corrupt
DEFAULT_CVES = [
    {
        "cve_id": "CVE-2024-21626",
        "title": "runc Container Escape",
        "severity": "CRITICAL",
        "cwe": "CWE-20",
        "description": "runc allows escape to the host namespace due to file descriptor leak.",
        "remediation": "Upgrade runc to version 1.1.12 or later.",
        "affected_component": "runc"
    },
    {
        "cve_id": "CVE-2024-3094",
        "title": "XZ Utils Backdoor",
        "severity": "CRITICAL",
        "cwe": "CWE-506",
        "description": "Malicious code was discovered in xz-utils that allows unauthorized SSH access.",
        "remediation": "Downgrade xz-utils to 5.4.6 or upgrade to non-backdoored version.",
        "affected_component": "xz-utils"
    },
    {
        "cve_id": "CVE-2023-38606",
        "title": "Apple iOS Kernel Remote Code Execution",
        "severity": "HIGH",
        "cwe": "CWE-269",
        "description": "A state management vulnerability in Kernel allowing unauthorized modification of hardware state.",
        "remediation": "Apply latest security updates from Apple.",
        "affected_component": "ios"
    },
    {
        "cve_id": "CVE-2023-44487",
        "title": "HTTP/2 Rapid Reset DDoS",
        "severity": "HIGH",
        "cwe": "CWE-400",
        "description": "HTTP/2 protocol allows rapid stream resets leading to denial of service (DDoS).",
        "remediation": "Apply HTTP/2 rate limiting or disable HTTP/2.",
        "affected_component": "http2"
    },
    {
        "cve_id": "CVE-2021-44228",
        "title": "Log4Shell Vulnerability",
        "severity": "CRITICAL",
        "cwe": "CWE-502",
        "description": "Apache Log4j2 JNDI features do not protect against attacker controlled LDAP and other JNDI related endpoints.",
        "remediation": "Upgrade Log4j2 to version 2.15.0 or later.",
        "affected_component": "log4j"
    }
]


class CVEDatabaseScanner(BaseScanner):
    """
    This class implements local-only Common Vulnerabilities and Exposures (CVE) database scanning.
    It reads from a bundled CVE JSON feed, fully satisfying the MEISSNER air-gap protocol.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name=name or "CVEDatabaseScanner",
            description=description or "Local-only CVE database scanner verifying against bundled CVE feed."
        )
        self.cves: List[Dict] = []
        self._load_cve_database()

    def _load_cve_database(self) -> None:
        """Load CVEs from the local JSON feed file, falling back to embedded defaults on failure."""
        db_path = pathlib.Path(__file__).parent / "cves.json"
        try:
            if db_path.exists():
                with open(db_path, "r", encoding="utf-8") as f:
                    self.cves = json.load(f)
                logger.info("Loaded %d CVEs from local feed.", len(self.cves))
            else:
                logger.warning("Local cves.json not found at %s. Falling back to embedded default list.", db_path)
                self.cves = DEFAULT_CVES.copy()
        except Exception as e:
            logger.error("Failed to load local cves.json: %s. Falling back to embedded default list.", e)
            self.cves = DEFAULT_CVES.copy()

    def get_vulnerabilities(self, max_results: int = 50, severity: str = None) -> List[Dict]:
        """
        Legacy-compatible method to retrieve vulnerabilities from the local database.
        
        :param max_results: (int) Maximum number of items to retrieve.
        :param severity: (str) If specified, filters results by severity level.
        :returns List[Dict]: List of matching CVE entries.
        """
        if severity and severity.upper() not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            raise ValueError("Valid severities are: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'")
        if max_results > 100:
            raise ValueError("Max results cannot exceed 100")

        filtered = self.cves
        if severity is not None:
            filtered = [c for c in filtered if c.get("severity", "").upper() == severity.upper()]

        return filtered[:max_results]

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """
        Execute the CVE matching scan against a target components string, host, or URL.
        
        Checks if the target or target hostname contains names of vulnerable components.
        """
        start_time = time.time()
        findings: List[Finding] = []
        status = "completed"

        # Parse host from target URL/IP/host safely
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path

        # Strip optional port suffix if specified in target URL (e.g. host:port)
        if ":" in host:
            host = host.split(":")[0]

        # Target validation to prevent command/path injection (CWE-78 / CWE-20)
        if not host or not re.match(r"^[a-zA-Z0-9_.-]+$", host):
            duration_ms = (time.time() - start_time) * 1000
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=duration_ms,
                status="failed",
            )

        try:
            # Match components against the loaded CVE list
            target_lower = host.lower()
            for cve in self.cves:
                component = cve.get("affected_component", "").lower()
                if component and component in target_lower:
                    try:
                        severity_val = Severity(cve.get("severity", "MEDIUM").upper())
                    except ValueError:
                        severity_val = Severity.MEDIUM

                    findings.append(
                        Finding(
                            title=f"Vulnerable component '{component}' matched {cve.get('cve_id')}",
                            severity=severity_val,
                            description=cve.get("description", "No description available."),
                            cwe=cve.get("cwe", "CWE-999"),
                            remediation=cve.get("remediation", "Update component immediately.")
                        )
                    )
        except Exception as e:
            logger.error("Error during CVE matching scan: %s", e)
            status = "failed"

        duration_ms = (time.time() - start_time) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status=status
        )

    def __str__(self) -> str:
        return f"{len(self.cves)} Vulnerabilities loaded in local CVE Database."
