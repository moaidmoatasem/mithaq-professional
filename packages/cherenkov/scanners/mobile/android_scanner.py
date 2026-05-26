"""Android Scanner"""

from typing import List

from cherenkov.core.base_scanner import Finding, Severity
from cherenkov.core.mobile_scanner import MobileScanner


class AndroidScanner(MobileScanner):
    """Scanner for Android APK files using static analysis logic."""

    def __init__(self):
        super().__init__(name="android", description="Android APK static analysis scanner")

    async def scan_file(self, file_path: str) -> List[Finding]:
        """Perform static analysis on an APK file."""
        findings = []

        # Simulate APK analysis (e.g., manifest checks, dex disassembly)
        # In a real implementation, we would call 'apktool' or 'androguard'

        # Mock finding: Debug mode enabled
        findings.append(
            Finding(
                title="Android Debug Mode Enabled",
                severity=Severity.HIGH,
                description="The APK has 'android:debuggable=true' in AndroidManifest.xml.",
                cwe="CWE-489",
                remediation="Set 'android:debuggable=false' in the manifest before production release.",
            )
        )

        # Mock finding: Insecure Permissions
        findings.append(
            Finding(
                title="Insecure Permissions: READ_EXTERNAL_STORAGE",
                severity=Severity.LOW,
                description="The app requests READ_EXTERNAL_STORAGE, which may expose sensitive user data.",
                cwe="CWE-276",
                remediation="Only request necessary permissions and use Scoped Storage where possible.",
            )
        )

        return findings
