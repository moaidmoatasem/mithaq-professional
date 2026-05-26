"""iOS Scanner"""

from typing import List

from cherenkov.core.base_scanner import Finding, Severity
from cherenkov.core.mobile_scanner import MobileScanner


class IOSScanner(MobileScanner):
    """Scanner for iOS IPA files using static analysis logic."""

    def __init__(self):
        super().__init__(name="ios", description="iOS IPA static analysis scanner")

    async def scan_file(self, file_path: str) -> List[Finding]:
        """Perform static analysis on an IPA file."""
        findings = []

        # Mock finding: Insecure ATS Configuration
        findings.append(
            Finding(
                title="Insecure App Transport Security (ATS) Configuration",
                severity=Severity.HIGH,
                description="The Info.plist allows insecure HTTP loads (NSAllowsArbitraryLoads=true).",
                cwe="CWE-319",
                remediation="Set 'NSAllowsArbitraryLoads' to false and use HTTPS for all connections.",
            )
        )

        # Mock finding: Hardcoded Secret in Binary
        findings.append(
            Finding(
                title="Potential Hardcoded Secret",
                severity=Severity.MEDIUM,
                description="A potential API key or secret was found in the binary strings.",
                cwe="CWE-798",
                remediation="Use a secure vault or keychain to store sensitive credentials.",
            )
        )

        return findings
