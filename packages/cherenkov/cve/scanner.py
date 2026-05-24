# packages/cherenkov/cve/scanner.py
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity
from .matcher import match_package_version


class CVEScanner(BaseScanner):
    """Scanner: Detect software versions and attach CVE matches."""

    def __init__(self):
        super().__init__(
            name="cve_scanner",
            description="Detects software versions and correlates with NVD CVE database",
        )

    async def scan(self, target: str, timeout: float = 30.0) -> ScanResult:
        """Scan target for software versions and match against CVE database.

        Queries the local NVD SQLite store for CVEs affecting detected packages.
        """
        findings = []
        packages = await self._detect_packages(target, timeout)

        for pkg in packages:
            pkg_name = pkg.get("name", "")
            pkg_version = pkg.get("version", "")
            if not pkg_name or not pkg_version:
                continue

            matches = match_package_version(pkg_name, pkg_version)
            for match in matches:
                severity = self._cvss_to_severity(float(match.get("cvss", 0)))
                findings.append(Finding(
                    title=f"{match['cve']}: {pkg_name} {pkg_version}",
                    severity=severity,
                    description=match.get("summary", ""),
                    cwe="CWE-1104",  # Use of Unmaintained Third-Party Components
                    remediation=f"Upgrade {pkg_name} to a non-vulnerable version",
                ))

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
        )

    async def _detect_packages(self, target: str, timeout: float) -> list[dict]:
        """Detect software packages/versions from target response.

        Currently uses HTTP headers to detect server-side technologies.
        Can be extended with more sophisticated fingerprinting.
        """
        packages = []
        try:
            resp = await self._http_request(target, timeout)
            server = resp.headers.get("Server", "")
            if server:
                packages.append({"name": server.split("/")[0], "version": server.split("/")[1] if "/" in server else ""})
            x_powered = resp.headers.get("X-Powered-By", "")
            if x_powered:
                parts = x_powered.split("/")
                packages.append({"name": parts[0], "version": parts[1] if len(parts) > 1 else ""})
        except Exception:
            pass
        return packages

    @staticmethod
    def _cvss_to_severity(cvss_score: float) -> Severity:
        """Convert CVSS 3.1 score to Finding severity."""
        if cvss_score >= 9.0:
            return Severity.CRITICAL
        elif cvss_score >= 7.0:
            return Severity.HIGH
        elif cvss_score >= 4.0:
            return Severity.MEDIUM
        else:
            return Severity.LOW
