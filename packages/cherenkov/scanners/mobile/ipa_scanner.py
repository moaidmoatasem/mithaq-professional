"""IPA unpacker + plist parser — static analysis of iOS IPA bundles"""

import plistlib
import zipfile
from typing import Optional

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class IpaScanner(BaseScanner):
    """Extract and audit Info.plist from iOS IPA archives"""

    def __init__(self):
        super().__init__(
            name="ipa",
            description="IPA bundle analysis — extract Info.plist, audit permissions and entitlements",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        import time as time_module

        start = time_module.monotonic()
        findings: list[Finding] = []

        plist_data = self._extract_plist(target)
        if plist_data is None:
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=(time_module.monotonic() - start) * 1000,
                status="completed",
            )

        findings.extend(self._audit_plist(plist_data))

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=(time_module.monotonic() - start) * 1000,
        )

    def _extract_plist(self, ipa_path: str) -> Optional[dict]:
        """Extract Info.plist from an IPA (zip) archive."""
        if ipa_path.startswith(("http://", "https://", "ftp://")):
            return None
        try:
            with zipfile.ZipFile(ipa_path, "r") as zf:
                plist_paths = [n for n in zf.namelist() if n.endswith("Info.plist")]
                if not plist_paths:
                    return None
                with zf.open(plist_paths[0]) as f:
                    return plistlib.load(f)
        except (zipfile.BadZipFile, plistlib.InvalidFileException, FileNotFoundError, OSError):
            return None

    def _audit_plist(self, plist: dict) -> list[Finding]:
        """Audit extracted plist for security-relevant settings."""
        findings: list[Finding] = []

        bundle_id = plist.get("CFBundleIdentifier", "unknown")
        bundle_version = plist.get("CFBundleShortVersionString", "unknown")

        if "NSAppTransportSecurity" in plist:
            ats = plist["NSAppTransportSecurity"]
            if ats.get("NSAllowsArbitraryLoads"):
                findings.append(
                    Finding(
                        title="NSAllowsArbitraryLoads Enabled",
                        severity=Severity.HIGH,
                        description=f"{bundle_id} v{bundle_version}: App Transport Security allows arbitrary HTTP loads, disabling HTTPS enforcement.",
                        cwe="CWE-319",
                        remediation="Remove NSAllowsArbitraryLoads or restrict to specific domains via NSExceptionDomains.",
                    )
                )

        if "NSExceptionDomains" in plist.get("NSAppTransportSecurity", {}):
            domains = plist["NSAppTransportSecurity"]["NSExceptionDomains"]
            for domain, config in domains.items():
                if config.get("NSIncludesSubdomains") and config.get(
                    "NSTemporaryExceptionAllowsInsecureHTTPLoads"
                ):
                    findings.append(
                        Finding(
                            title="Insecure ATS Exception Domain",
                            severity=Severity.MEDIUM,
                            description=f"{bundle_id}: Domain '{domain}' allows insecure HTTP loads with subdomain wildcard.",
                            cwe="CWE-319",
                            remediation="Remove NSTemporaryExceptionAllowsInsecureHTTPLoads or restrict to HTTPS-only.",
                        )
                    )

        if "UIRequiresFullScreen" not in plist:
            pass

        exposed_schemes = plist.get("CFBundleURLTypes", [])
        for scheme_entry in exposed_schemes:
            schemes = scheme_entry.get("CFBundleURLSchemes", [])
            for scheme in schemes:
                if scheme.lower() in ("fb", "twitter", "telegram", "vk", "snapchat"):
                    findings.append(
                        Finding(
                            title="Exposed URL Scheme",
                            severity=Severity.LOW,
                            description=f"{bundle_id}: Custom URL scheme '{scheme}' exposed, potential for scheme hijacking.",
                            cwe="CWE-200",
                            remediation="Validate incoming URLs and restrict scheme handling to expected sources.",
                        )
                    )

        return findings
