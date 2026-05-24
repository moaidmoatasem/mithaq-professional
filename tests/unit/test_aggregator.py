import unittest

from cherenkov.core.aggregator import ScanAggregator
from cherenkov.core.base_scanner import Finding, ScanResult, Severity


class TestScanAggregator(unittest.TestCase):
    def test_aggregator_empty(self):
        """Test aggregation with empty results list"""
        result = ScanAggregator.aggregate([])
        self.assertEqual(result.target, "")
        self.assertEqual(result.scanner_name, "aggregated")
        self.assertEqual(result.findings, [])
        self.assertEqual(result.duration_ms, 0.0)
        self.assertEqual(result.status, "completed")

    def test_aggregator_merges(self):
        """Test that aggregator merges findings and sums durations"""
        finding1 = Finding(
            title="SQL Injection",
            severity=Severity.HIGH,
            description="SQL Injection in parameter id",
            cwe="CWE-89",
            remediation="Use parameterized queries",
        )
        finding2 = Finding(
            title="Reflected XSS",
            severity=Severity.MEDIUM,
            description="Reflected XSS in parameter name",
            cwe="CWE-79",
            remediation="HTML encode inputs",
        )

        res1 = ScanResult(
            target="http://example.com",
            scanner_name="sqli_scanner",
            findings=[finding1],
            duration_ms=120.0,
        )
        res2 = ScanResult(
            target="http://example.com",
            scanner_name="xss_scanner",
            findings=[finding2],
            duration_ms=80.0,
        )

        merged = ScanAggregator.aggregate([res1, res2])
        self.assertEqual(merged.target, "http://example.com")
        self.assertEqual(merged.scanner_name, "aggregated")
        self.assertEqual(len(merged.findings), 2)
        self.assertEqual(merged.duration_ms, 200.0)

        # First in list should be SQL Injection (HIGH severity) then XSS (MEDIUM severity)
        self.assertEqual(merged.findings[0].title, "SQL Injection")
        self.assertEqual(merged.findings[1].title, "Reflected XSS")

    def test_aggregator_severity_sort(self):
        """Test sorting of findings by severity (CRITICAL down to INFO)"""
        finding_info = Finding(
            title="Info Leak",
            severity=Severity.INFO,
            description="Information disclosure",
            cwe="CWE-200",
            remediation="None needed",
        )
        finding_critical = Finding(
            title="Remote Code Execution",
            severity=Severity.CRITICAL,
            description="RCE vulnerability",
            cwe="CWE-94",
            remediation="Patch system",
        )
        finding_medium = Finding(
            title="Medium Leak",
            severity=Severity.MEDIUM,
            description="Medium vulnerability",
            cwe="CWE-200",
            remediation="Fix it",
        )

        res = ScanResult(
            target="http://example.com",
            scanner_name="multi_scanner",
            findings=[finding_info, finding_critical, finding_medium],
            duration_ms=100.0,
        )

        merged = ScanAggregator.aggregate([res])
        self.assertEqual(len(merged.findings), 3)
        self.assertEqual(merged.findings[0].severity, Severity.CRITICAL)
        self.assertEqual(merged.findings[1].severity, Severity.MEDIUM)
        self.assertEqual(merged.findings[2].severity, Severity.INFO)

    def test_aggregator_deduplication(self):
        """Test deduplication of findings keeping the highest severity"""
        finding_low = Finding(
            title="Vulnerable Header",
            severity=Severity.LOW,
            description="Missing security header",
            cwe="CWE-693",
            remediation="Add header",
        )
        finding_high = Finding(
            title="Vulnerable Header",
            severity=Severity.HIGH,
            description="Missing security header",
            cwe="CWE-693",
            remediation="Add header",
        )

        # Same target, same scanner_name, same title -> should deduplicate
        res1 = ScanResult(
            target="http://example.com",
            scanner_name="header_scanner",
            findings=[finding_low],
            duration_ms=50.0,
        )
        res2 = ScanResult(
            target="http://example.com",
            scanner_name="header_scanner",
            findings=[finding_high],
            duration_ms=50.0,
        )

        merged = ScanAggregator.aggregate([res1, res2])
        self.assertEqual(len(merged.findings), 1)
        self.assertEqual(merged.findings[0].severity, Severity.HIGH)


if __name__ == "__main__":
    unittest.main()
