"""Scan Result Aggregator Pipeline"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from cherenkov.core.base_scanner import Finding, ScanResult, Severity
from cherenkov.core.storage.database import save_trace

logger = logging.getLogger("cherenkov.aggregator")

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
                trace_hash="",
                trace_hashes=[],
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

        # Collect and deduplicate trace hashes from results and findings
        trace_hashes_set = set()
        for r in results:
            if r.trace_hash:
                trace_hashes_set.add(r.trace_hash)
            if r.trace_hashes:
                for h in r.trace_hashes:
                    if h:
                        trace_hashes_set.add(h)
            for f in r.findings:
                if f.trace_hash:
                    trace_hashes_set.add(f.trace_hash)

        sorted_trace_hashes = sorted(list(trace_hashes_set))

        # Generate a valid 64-char SHA-256 trace hash for the aggregated result
        iso_timestamp = datetime.now(timezone.utc).isoformat()
        if sorted_trace_hashes:
            hash_input = "".join(sorted_trace_hashes)
        else:
            hash_input = target + iso_timestamp

        trace_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        # Persist the aggregator trace in the WAL database
        try:
            save_trace(
                finding_id=trace_hash,
                exploit_command="scan_aggregation",
                stdout="Scan aggregation succeeded.",
                stderr="",
                exit_code=0,
                trace_hash=trace_hash,
                timestamp=iso_timestamp,
                shred_receipt={"files_erased": []},
            )
        except Exception as e:
            logger.warning("Failed to persist aggregator trace: %s", e)

        return ScanResult(
            target=target,
            scanner_name=scanner_name,
            findings=sorted_findings,
            duration_ms=total_duration,
            status="completed",
            trace_hash=trace_hash,
            trace_hashes=sorted_trace_hashes,
        )
