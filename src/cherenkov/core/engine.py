"""Async Scan Engine - Runs scanners concurrently"""

import asyncio
import time
from typing import Dict, List

from .base_scanner import ScanResult
from .registry import ScannerRegistry


class ScanEngine:
    """Async scan engine for concurrent scanner execution"""

    def __init__(self, registry: ScannerRegistry):
        self.registry = registry
        self.concurrency_limit = 10

    async def scan_single(
        self, scanner_name: str, target: str, timeout: float = 10.0
    ) -> ScanResult:
        """Run single scanner"""
        scanner_class = self.registry.get_scanner(scanner_name)
        scanner = scanner_class()

        start_time = time.time()
        result = await scanner.scan(target, timeout)
        result.duration_ms = (time.time() - start_time) * 1000

        return result

    async def scan_all(
        self,
        target: str,
        scanners: List[str] = None,
        timeout: float = 10.0,
        max_concurrent: int = 10,
    ) -> Dict[str, ScanResult]:
        """Run all scanners concurrently"""
        if scanners is None:
            scanners = self.registry.list_scanners()

        semaphore = asyncio.Semaphore(max_concurrent)

        async def scan_with_semaphore(scanner_name: str) -> ScanResult:
            async with semaphore:
                return await self.scan_single(scanner_name, target, timeout)

        tasks = [scan_with_semaphore(s) for s in scanners]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scan_results = {}
        for scanner_name, result in zip(scanners, results, strict=False):
            if isinstance(result, Exception):
                scan_results[scanner_name] = ScanResult(
                    target=target,
                    scanner_name=scanner_name,
                    status="failed",
                    findings=[],
                )
            else:
                scan_results[scanner_name] = result

        return scan_results
