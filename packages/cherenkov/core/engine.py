import asyncio
import logging
import time
from typing import Callable, Dict, List, Optional
from urllib.parse import urlparse

from .base_scanner import ScanResult
from .registry import ScannerRegistry

logger = logging.getLogger(__name__)


class ScanEngine:
    """Async scan engine for concurrent scanner execution with progress tracking"""

    def __init__(self, registry: ScannerRegistry):
        self.registry = registry
        self.concurrency_limit = 10

    async def scan_single(
        self, scanner_name: str, target: str, timeout: float = 10.0, raise_on_failure: bool = False
    ) -> ScanResult:
        """Run single scanner with isolated timeout and error handling"""
        try:
            scanner_class = self.registry.get_scanner(scanner_name)
            scanner = scanner_class(scanner_class.__name__, "")

            start_time = time.time()
            # Wrap in wait_for as a safety layer above the scanner's own timeout logic
            result = await asyncio.wait_for(scanner.scan(target, timeout), timeout=timeout + 2)
            result.duration_ms = (time.time() - start_time) * 1000
            return result
        except asyncio.TimeoutError:
            logger.warning("Scanner %s timed out on %s", scanner_name, target)
            if raise_on_failure:
                raise
            return ScanResult(
                target=target,
                scanner_name=scanner_name,
                status="timeout",
                findings=[],
            )
        except Exception as exc:
            logger.error("Scanner %s failed: %s", scanner_name, exc)
            if raise_on_failure:
                raise
            return ScanResult(
                target=target,
                scanner_name=scanner_name,
                status="failed",
                findings=[],
            )

    async def scan_all(
        self,
        target: str,
        scanners: List[str] = None,
        timeout: float = 10.0,
        max_concurrent: int = 10,
        on_progress: Optional[Callable[[str, ScanResult], None]] = None,
    ) -> Dict[str, ScanResult]:
        """Run all scanners concurrently with concurrency limiting and progress updates"""
        if scanners is None:
            scanners = self.registry.list_scanners()

        semaphore = asyncio.Semaphore(max_concurrent)

        async def scan_with_semaphore(scanner_name: str) -> ScanResult:
            async with semaphore:
                # Target-level circuit breaker: if the target is failing consistently, stop scanning
                from .circuit_breaker import default_registry, CircuitBreakerConfig
                
                target_host = urlparse(target).netloc or "default"
                breaker = default_registry.get_or_create(
                    f"target:{target_host}", 
                    CircuitBreakerConfig(failure_threshold=3, recovery_timeout=60)
                )

                try:
                    result = await breaker.execute_async(self.scan_single, scanner_name, target, timeout, raise_on_failure=True)
                    if on_progress:
                        if asyncio.iscoroutinefunction(on_progress):
                            await on_progress(scanner_name, result)
                        else:
                            on_progress(scanner_name, result)
                    return result
                except Exception as exc:
                    from .circuit_breaker import CircuitOpenError
                    if isinstance(exc, CircuitOpenError):
                        logger.warning("Circuit breaker blocked scan for %s: %s", target_host, exc)
                        status = "circuit_open"
                    else:
                        logger.error("Scanner %s failed for %s: %s", scanner_name, target_host, exc)
                        status = "failed"
                    
                    res = ScanResult(
                        target=target,
                        scanner_name=scanner_name,
                        status=status,
                        findings=[],
                    )
                    if on_progress:
                        if asyncio.iscoroutinefunction(on_progress):
                            await on_progress(scanner_name, res)
                        else:
                            on_progress(scanner_name, res)
                    return res

        tasks = [scan_with_semaphore(s) for s in scanners]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        return {s: r for s, r in zip(scanners, results, strict=False)}
