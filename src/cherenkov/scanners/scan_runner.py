#!/usr/bin/env python3
"""
Unified Scanner Runner
Runs all discovered scanners on a target using the ScannerRegistry and EventBus.
"""

import asyncio
import sys
from datetime import datetime
from typing import Any, Dict

from cherenkov.core.events import event_bus
from cherenkov.core.registry import ScannerRegistry
from cherenkov.result_persistence import ResultStore


class UnifiedScanner:
    """Run all available scanners on a target using event-driven architecture"""

    def __init__(self, target_url: str):
        self.target = target_url
        self.registry = ScannerRegistry()
        self.results = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "scans": [],
        }

        # Subscribe to events for tracking/logging
        event_bus.subscribe("scan_started", self._on_scan_started)
        event_bus.subscribe("scan_completed", self._on_scan_completed)

    def _on_scan_started(self, scanner_name: str, target: str):
        print(f"🚀 Started {scanner_name} against {target}")

    def _on_scan_completed(self, scanner_name: str, target: str, findings_count: int):
        print(f"✅ Completed {scanner_name} - Found {findings_count} vulnerabilities")

    async def run_all_scans(self) -> Dict[str, Any]:
        """Execute all scanners asynchronously"""
        print("\n" + "=" * 70)
        print("🔍 cherenkov UNIFIED SECURITY SCANNER (EVENT-DRIVEN)")
        print("=" * 70)
        print(f"Target: {self.target}")

        available_scanners = self.registry.list_scanners()
        print(
            f"\n📦 Found {len(available_scanners)} registered scanners: {', '.join(available_scanners)}\n"
        )

        tasks = []
        # Create and run scanners concurrently
        for scanner_name in available_scanners:
            scanner = self.registry.create_scanner(scanner_name)
            tasks.append(self._run_single_scanner(scanner_name, scanner))

        await asyncio.gather(*tasks)

        return self.results

    async def _run_single_scanner(self, name: str, scanner):
        await event_bus.publish_async("scan_started", scanner_name=name, target=self.target)

        try:
            # Execute standard scan interface
            result = await scanner.scan(self.target)

            # Record result
            scan_data = {
                "scanner": name,
                "status": result.status,
                "duration_ms": result.duration_ms,
                "findings_count": len(result.findings),
                "findings": [f.model_dump() for f in result.findings],
            }
            self.results["scans"].append(scan_data)

            await event_bus.publish_async(
                "scan_completed",
                scanner_name=name,
                target=self.target,
                findings_count=len(result.findings),
            )
        except Exception as e:
            print(f"❌ Error in {name}: {str(e)}")
            self.results["scans"].append({"scanner": name, "status": "error", "error": str(e)})

    def save_report(self):
        """Save scan report using decoupled ResultStore"""
        store = ResultStore()
        filepath = store.save_result("unified_scan", self.results)
        print(f"\n📄 Report saved via ResultStore to: {filepath}")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_runner.py <target_url>")
        sys.exit(1)

    scanner = UnifiedScanner(sys.argv[1])
    await scanner.run_all_scans()
    scanner.save_report()


if __name__ == "__main__":
    asyncio.run(main())
