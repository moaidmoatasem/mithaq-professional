"""Scan Result Aggregator Pipeline"""

from typing import Dict, List, Tuple

from cherenkov.core.base_scanner import Finding, ScanResult, Severity

# Severity priority order (higher value = more severe)
SEVERITY_ORDER = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
    Severity.INFO: 0,
}


class ScanAggregator:
    """Merges and deduplicates ScanResults from multiple scanners"""

    @staticmethod
    def aggregate(results: List[ScanResult]) -> ScanResult:
        """
        Merge findings from N parallel scanner results into one unified ScanResult.
        Deduplicates findings by (target, scanner_name, finding_title).
        Keeps the highest severity finding when deduplicating.
        Sums duration_ms from all results.
        Sorts findings by severity with CRITICAL first down to INFO.
        """
        if not results:
            return ScanResult(
                target="",
                scanner_name="aggregated",
                findings=[],
                duration_ms=0.0,
                status="completed",
            )

        target = results[0].target
        scanner_name = "aggregated"
        total_duration = sum(r.duration_ms for r in results)

        unique_findings: Dict[Tuple[str, str, str], Finding] = {}

        for result in results:
            for finding in result.findings:
                key = (result.target, result.scanner_name, finding.title)

                # If key not seen yet, or if this finding has a higher severity, keep it
                if key not in unique_findings:
                    unique_findings[key] = finding
                else:
                    existing_sev = SEVERITY_ORDER.get(unique_findings[key].severity, -1)
                    new_sev = SEVERITY_ORDER.get(finding.severity, -1)
                    if new_sev > existing_sev:
                        unique_findings[key] = finding

        # Sort findings by severity (CRITICAL down to INFO)
        sorted_findings = sorted(
            unique_findings.values(), key=lambda f: SEVERITY_ORDER.get(f.severity, -1), reverse=True
        )

        # If any input result failed, set status to failed or completed?
        # Let's check if there is an explicit requirement. The instruction says:
        # "Merged ScanResult uses target from first result and scanner_name equals aggregated."
        # Status can default to "completed".
        return ScanResult(
            target=target,
            scanner_name=scanner_name,
            findings=sorted_findings,
            duration_ms=total_duration,
            status="completed",
        )
