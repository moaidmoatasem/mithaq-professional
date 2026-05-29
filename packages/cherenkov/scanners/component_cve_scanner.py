"""Component CVE Scanner — matches target hostname/URL components against CVE database"""

from __future__ import annotations

import json
import logging
import pathlib
import re
import time
from typing import Dict, List
from urllib.parse import urlparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.component_cve")

_COMPONENT_CVES: list[Dict] = [
    {
        "cve_id": "CVE-2024-21626",
        "title": "runc Container Escape",
        "severity": "CRITICAL",
        "cwe": "CWE-20",
        "description": "runc allows escape to the host namespace due to file descriptor leak.",
        "remediation": "Upgrade runc to version 1.1.12 or later.",
        "components": ["runc", "docker", "containerd"],
    },
    {
        "cve_id": "CVE-2024-3094",
        "title": "XZ Utils Backdoor",
        "severity": "CRITICAL",
        "cwe": "CWE-506",
        "description": "Malicious code discovered in xz-utils allowing unauthorized SSH access.",
        "remediation": "Downgrade xz-utils to 5.4.6 or upgrade to patched version.",
        "components": ["xz-utils", "xz", "liblzma"],
    },
    {
        "cve_id": "CVE-2023-44487",
        "title": "HTTP/2 Rapid Reset DDoS",
        "severity": "HIGH",
        "cwe": "CWE-400",
        "description": "HTTP/2 protocol allows rapid stream resets leading to denial of service.",
        "remediation": "Apply HTTP/2 rate limiting or disable HTTP/2.",
        "components": ["http2", "nginx", "apache", "envoy", "gunicorn"],
    },
    {
        "cve_id": "CVE-2021-44228",
        "title": "Log4Shell",
        "severity": "CRITICAL",
        "cwe": "CWE-502",
        "description": "Apache Log4j2 JNDI features do not protect against attacker-controlled endpoints.",
        "remediation": "Upgrade Log4j2 to version 2.15.0 or later.",
        "components": ["log4j", "log4j2", "log4j-core", "elasticsearch", "solr"],
    },
    {
        "cve_id": "CVE-2023-38606",
        "title": "Apple iOS Kernel RCE",
        "severity": "HIGH",
        "cwe": "CWE-269",
        "description": "State management vulnerability in Kernel allowing unauthorized hardware state modification.",
        "remediation": "Apply latest security updates from Apple.",
        "components": ["ios", "iphone", "ipados", "webkit"],
    },
    {
        "cve_id": "CVE-2023-49070",
        "title": "Apache OFBiz RCE",
        "severity": "CRITICAL",
        "cwe": "CWE-94",
        "description": "Pre-auth RCE in Apache OFBiz via XML-RPC.",
        "remediation": "Upgrade Apache OFBiz to 18.12.10 or later.",
        "components": ["ofbiz", "apache-ofbiz"],
    },
    {
        "cve_id": "CVE-2023-46604",
        "title": "Apache ActiveMQ RCE",
        "severity": "CRITICAL",
        "cwe": "CWE-502",
        "description": "Remote code execution via deserialization in Apache ActiveMQ.",
        "remediation": "Upgrade ActiveMQ to 5.15.16, 5.16.7, 5.17.6, or 5.18.3.",
        "components": ["activemq", "apache-activemq"],
    },
    {
        "cve_id": "CVE-2023-50164",
        "title": "Apache Struts RCE",
        "severity": "CRITICAL",
        "cwe": "CWE-20",
        "description": "RCE in Apache Struts via file upload parameter manipulation.",
        "remediation": "Upgrade Apache Struts to 2.5.33 or 6.3.0.2.",
        "components": ["struts", "apache-struts"],
    },
    {
        "cve_id": "CVE-2024-27198",
        "title": "JetBrains TeamCity Auth Bypass",
        "severity": "CRITICAL",
        "cwe": "CWE-287",
        "description": "Authentication bypass in TeamCity allowing admin access.",
        "remediation": "Upgrade JetBrains TeamCity to 2023.11.4 or later.",
        "components": ["teamcity", "jetbrains-teamcity"],
    },
    {
        "cve_id": "CVE-2021-3449",
        "title": "OpenSSL DoS",
        "severity": "HIGH",
        "cwe": "CWE-476",
        "description": "NULL pointer dereference in OpenSSL during renegotiation.",
        "remediation": "Upgrade OpenSSL to 1.1.1j or later.",
        "components": ["openssl", "libssl"],
    },
]


class ComponentCVEScanner(BaseScanner):
    """Matches target hostname/URL components against a local CVE database by component name."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "component_cve_scanner",
            description
            or "Local-only CVE scanner matching target hostname components against known vulnerable software (MEISSNER air-gapped)",
        )
        self.cve_db: List[Dict] = []
        self._load_cve_database()

    def _load_cve_database(self) -> None:
        db_path = pathlib.Path(__file__).parent / "cves.json"
        try:
            if db_path.exists():
                with open(db_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.cve_db = raw
                logger.info("Loaded %d CVEs from local feed.", len(self.cve_db))
            else:
                self.cve_db = _COMPONENT_CVES.copy()
        except Exception as e:
            logger.error("Failed to load cves.json: %s. Using embedded defaults.", e)
            self.cve_db = _COMPONENT_CVES.copy()

    def _get_components(self, cve: Dict) -> List[str]:
        components = cve.get("components", None)
        if components is not None:
            if isinstance(components, str):
                return [components]
            return components
        affected = cve.get("affected_component", None)
        if affected is not None:
            return [affected] if isinstance(affected, str) else affected
        return []

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []
        status = "completed"

        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        if ":" in host:
            host = host.split(":")[0]

        if not host or not re.match(r"^[a-zA-Z0-9_.-]+$", host):
            duration_ms = (time.monotonic() - start) * 1000
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=duration_ms,
                status="failed",
            )

        try:
            target_lower = host.lower()
            for cve in self.cve_db:
                components = self._get_components(cve)
                for component in components:
                    if component.lower() in target_lower:
                        try:
                            severity_val = Severity(cve.get("severity", "MEDIUM").upper())
                        except ValueError:
                            severity_val = Severity.MEDIUM

                        findings.append(
                            Finding(
                                title=f"Vulnerable component '{component}' matched {cve['cve_id']}",
                                severity=severity_val,
                                description=cve.get("description", "No description available."),
                                cwe=cve.get("cwe", "CWE-999"),
                                remediation=cve.get("remediation", "Update component immediately."),
                            )
                        )
                        break

            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                try:
                    response = await client.get(target, follow_redirects=True)
                    server_header = response.headers.get("server", "")
                    via_header = response.headers.get("via", "")
                    x_powered_by = response.headers.get("x-powered-by", "")
                    headers_text = f"{server_header} {via_header} {x_powered_by}".lower()

                    for cve in self.cve_db:
                        components = self._get_components(cve)
                        for component in components:
                            if component.lower() in headers_text:
                                try:
                                    severity_val = Severity(cve.get("severity", "MEDIUM").upper())
                                except ValueError:
                                    severity_val = Severity.MEDIUM

                                findings.append(
                                    Finding(
                                        title=f"Response header reveals vulnerable component '{component}' ({cve['cve_id']})",
                                        severity=severity_val,
                                        description=(
                                            f"HTTP response headers disclose the presence of "
                                            f"'{component}' which is associated with {cve['cve_id']}. "
                                            f"{cve.get('description', '')}"
                                        ),
                                        cwe=cve.get("cwe", "CWE-999"),
                                        remediation=cve.get(
                                            "remediation", "Update component immediately."
                                        ),
                                    )
                                )
                                break
                except (httpx.RequestError, httpx.TimeoutException):
                    pass

        except Exception as e:
            logger.error("ComponentCVEScanner error for %s: %s", target, e)
            status = "failed"

        duration_ms = (time.monotonic() - start) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status=status,
        )
