"""
Unified Scanner Runner
Runs all discovered scanners on a target using the ScannerRegistry and EventBus.
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from cherenkov.core.events import EventBus
from cherenkov.core.events import event_bus as _global_event_bus
from cherenkov.core.registry import ScannerRegistry
from cherenkov.orchestration.result_persistence import ResultStore

logger = logging.getLogger(__name__)


class UnifiedScanner:
    """Run all available scanners on a target using event-driven architecture."""

    def __init__(self, target_url: str, event_bus: EventBus | None = None) -> None:
        self.target = target_url
        self.registry = ScannerRegistry()
        self._event_bus = event_bus or _global_event_bus
        self.results: Dict[str, Any] = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "scans": [],
        }
        self._event_bus.subscribe("scan_started", self._on_scan_started)
        self._event_bus.subscribe("scan_completed", self._on_scan_completed)

    def _on_scan_started(self, scanner_name: str, target: str) -> None:
        logger.info("Started %s against %s", scanner_name, target)

    def _on_scan_completed(self, scanner_name: str, target: str, findings_count: int) -> None:
        logger.info("Completed %s - Found %d vulnerabilities", scanner_name, findings_count)

    async def run_all_scans(self) -> Dict[str, Any]:
        """Execute all scanners asynchronously."""
        available_scanners = self.registry.list_scanners()
        logger.info("Found %d registered scanners: %s", len(available_scanners), available_scanners)

        tasks = []
        for scanner_name in available_scanners:
            scanner = self.registry.create_scanner(scanner_name)
            tasks.append(self._run_single_scanner(scanner_name, scanner))

        await asyncio.gather(*tasks)
        return self.results

    async def _run_single_scanner(self, name: str, scanner: Any) -> None:
        await self._event_bus.publish_async("scan_started", scanner_name=name, target=self.target)

        try:
            result = await scanner.scan(self.target)
            scan_data = {
                "scanner": name,
                "status": result.status,
                "duration_ms": result.duration_ms,
                "findings_count": len(result.findings),
                "findings": [f.model_dump() for f in result.findings],
            }
            self.results["scans"].append(scan_data)

            await self._event_bus.publish_async(
                "scan_completed",
                scanner_name=name,
                target=self.target,
                findings_count=len(result.findings),
            )
        except Exception as e:
            logger.error("Error in %s: %s", name, e)
            self.results["scans"].append({"scanner": name, "status": "error", "error": str(e)})

    def save_report(self) -> None:
        """Save scan report using ResultStore."""
        store = ResultStore()
        filepath = store.save_result("unified_scan", self.results)
        logger.info("Report saved to %s", filepath)


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scan_runner.py <target_url>", file=sys.stderr)
        sys.exit(1)

    scanner = UnifiedScanner(sys.argv[1])
    await scanner.run_all_scans()
    scanner.save_report()


if __name__ == "__main__":
    asyncio.run(main())
