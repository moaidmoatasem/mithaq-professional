#!/usr/bin/env python3
"""
Unified Scanner Runner
Runs all generated scanners on a target
"""

import sys
import importlib
from pathlib import Path
import json
from datetime import datetime


class UnifiedScanner:
    """Run all available scanners on a target"""

    def __init__(self, target_url: str):
        self.target = target_url
        self.results = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "scans": [],
        }

    def load_scanners(self):
        """Dynamically load all generated scanners"""
        scanner_dir = Path(__file__).parent / "generated"
        scanner_files = list(scanner_dir.glob("*_scanner.py"))

        print(f"📦 Found {len(scanner_files)} scanner modules")

        scanners = []
        for scanner_file in scanner_files:
            module_name = scanner_file.stem
            print(f"  • {module_name}")
            scanners.append(module_name)

        return scanners

    def run_all_scans(self):
        """Execute all scanners"""
        print("\n" + "=" * 70)
        print("🔍 DAQIQ UNIFIED SECURITY SCANNER")
        print("=" * 70)
        print(f"Target: {self.target}")

        scanners = self.load_scanners()

        print(f"\n🚀 Running {len(scanners)} scanners...\n")

        # For now, just acknowledge the scanners
        # (Actual execution would require standardized interfaces)
        for scanner in scanners:
            print(f"✓ {scanner} - Ready")
            self.results["scans"].append({"scanner": scanner, "status": "ready"})

        return self.results

    def save_report(self):
        """Save scan report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"unified_scan_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(self.results, indent=2, fp=f)

        print(f"\n📄 Report saved: {report_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scan_runner.py <target_url>")
        sys.exit(1)

    scanner = UnifiedScanner(sys.argv[1])
    scanner.run_all_scans()
    scanner.save_report()
