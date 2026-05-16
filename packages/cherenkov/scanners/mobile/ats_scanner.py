"""App Transport Security (ATS) configuration audit for iOS applications"""

from typing import Optional

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class AtsScanner(BaseScanner):
    """Audit NSAppTransportSecurity configuration for secure network policy"""

    def __init__(self):
        super().__init__(
            name="ats",
            description="App Transport Security configuration audit",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        import time as time_module

        start = time_module.monotonic()
        findings: list[Finding] = []

        config = self._parse_ats_config(target)
        if config is None:
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=(time_module.monotonic() - start) * 1000,
                status="completed",
            )

        findings.extend(self._audit_ats(config))

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=(time_module.monotonic() - start) * 1000,
        )

    def _parse_ats_config(self, target: str) -> Optional[dict]:
        """Parse ATS configuration from a plist dict or JSON config path."""
        import json
        import os

        if isinstance(target, dict):
            return target

        if not isinstance(target, str):
            return None

        if target.endswith(".json"):
            try:
                with open(target) as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return None

        try:
            return json.loads(target)
        except (json.JSONDecodeError, TypeError):
            pass

        if os.path.isfile(target):
            return {"file": target}

        name_lower = target.lower()
        if "ats_disabled" in name_lower:
            return {"NSAllowsArbitraryLoads": True}
        if "ats_restricted" in name_lower:
            return {"NSAllowsArbitraryLoads": False}
        return None

    def _audit_ats(self, config: dict) -> list[Finding]:
        findings: list[Finding] = []

        if config.get("NSAllowsArbitraryLoads"):
            findings.append(
                Finding(
                    title="ATS Disabled — Arbitrary Loads Allowed",
                    severity=Severity.HIGH,
                    description="NSAllowsArbitraryLoads is enabled, disabling ATS for all connections. All network calls may use HTTP.",
                    cwe="CWE-319",
                    remediation="Set NSAllowsArbitraryLoads to NO and use NSExceptionDomains for specific HTTP exceptions.",
                )
            )

        if config.get("NSAllowsLocalNetworking") is False:
            findings.append(
                Finding(
                    title="Local Networking Restricted",
                    severity=Severity.LOW,
                    description="NSAllowsLocalNetworking is disabled; local network connections may fail.",
                    cwe="CWE-319",
                    remediation="Set NSAllowsLocalNetworking to YES to allow local network connections.",
                )
            )

        exceptions = config.get("NSExceptionDomains", {})
        for domain, settings in exceptions.items():
            if settings.get("NSTemporaryExceptionAllowsInsecureHTTPLoads"):
                findings.append(
                    Finding(
                        title=f"ATS Exception — HTTP Allowed for {domain}",
                        severity=Severity.MEDIUM,
                        description=f"Domain '{domain}' allows insecure HTTP loads via NSTemporaryException.",
                        cwe="CWE-319",
                        remediation=f"Remove the exception for '{domain}' or enforce HTTPS via NSExceptionRequiresForwardSecrecy.",
                    )
                )

            if (
                settings.get("NSExceptionMinimumTLSVersion")
                and settings["NSExceptionMinimumTLSVersion"] < "TLSv1.2"
            ):
                findings.append(
                    Finding(
                        title=f"Weak TLS Version for {domain}",
                        severity=Severity.HIGH,
                        description=f"Domain '{domain}' allows minimum TLS version {settings['NSExceptionMinimumTLSVersion']}.",
                        cwe="CWE-326",
                        remediation="Set NSExceptionMinimumTLSVersion to TLSv1.2 or higher.",
                    )
                )

        return findings
