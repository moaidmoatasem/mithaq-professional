"""
MobileScanner — abstract base class for mobile application scanners.

Mobile scanners operate on file paths (APK / IPA) rather than URLs.
The scan() entry point treats 'target' as a file path and delegates
to scan_file(), wrapping the result in a ScanResult.
"""

from __future__ import annotations

import logging
import time
from abc import abstractmethod
from typing import List

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult

logger = logging.getLogger("cherenkov.scanners.mobile")


class MobileScanner(BaseScanner):
    """
    Base class for mobile (APK / IPA) static-analysis scanners.

    Subclasses implement scan_file(file_path) → List[Finding].
    The scan() method calls scan_file(target) so the scanner integrates
    transparently with ScannerRegistry and ScanEngine.
    """

    @abstractmethod
    async def scan_file(self, file_path: str) -> List[Finding]:
        """
        Analyse a mobile application file.

        Args:
            file_path: Path to the APK or IPA file to analyse.

        Returns:
            List of Finding objects describing identified issues.
        """

    async def scan(self, target: str, timeout: float = 30.0) -> ScanResult:
        """
        Entry point compatible with BaseScanner / ScanEngine.

        'target' is treated as a file path for mobile scanners.
        Network timeout is not applicable but kept for interface compatibility.
        """
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            findings = await self.scan_file(target)
        except FileNotFoundError:
            logger.debug("%s: target file not found — %s", self.name, target)
        except Exception as exc:
            logger.debug("%s: scan_file degraded for %s: %s", self.name, target, exc)

        duration_ms = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
