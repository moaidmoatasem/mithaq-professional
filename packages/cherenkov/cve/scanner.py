# packages/cherenkov/cve/scanner.py
from cherenkov.core.base_scanner import BaseScanner, Finding, Severity
from .matcher import match_package_version

class CVEScanner(BaseScanner):
    """Scanner: Detect software versions and attach CVE matches."""
    
    id = "cve-scanner"
    name = "CVE Version Matcher"
    description = "Detects software versions in findings and correlates with NVD CVE database"
    version = "1.0.0"
    
    def execute(self, target, context=None):
        """
        Scan target for software versions and match against CVE database.
        
        Args:
            target: URL or hostname to scan
            context: Dict with optional "packages" key containing [{"name": "...", "version": "..."}, ...]
        
        Returns:
            List of Finding objects for matched CVEs
        """
        if context is None:
            context = {}
        
        findings = []
        packages = context.get("packages", [])
        
        for pkg in packages:
            pkg_name = pkg.get("name", "")
            pkg_version = pkg.get("version", "")
            
            if not pkg_name or not pkg_version:
                continue
            
            # Match against CVE database
            matches = match_package_version(pkg_name, pkg_version)
            
            for match in matches:
                # Create a Finding for each CVE
                severity = self._cvss_to_severity(match["cvss"])
                finding = Finding(
                    scanner_id=self.id,
                    title=f"{match['cve']}: {pkg_name} {pkg_version}",
                    description=match["summary"],
                    severity=severity,
                    evidence={
                        "cve_id": match["cve"],
                        "package": pkg_name,
                        "version": pkg_version,
                        "cvss_score": match["cvss"]
                    }
                )
                findings.append(finding)
        
        return findings
    
    @staticmethod
    def _cvss_to_severity(cvss_score):
        """Convert CVSS 3.1 score to Finding severity."""
        if cvss_score >= 9.0:
            return Severity.CRITICAL
        elif cvss_score >= 7.0:
            return Severity.HIGH
        elif cvss_score >= 4.0:
            return Severity.MEDIUM
        else:
            return Severity.LOW