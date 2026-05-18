import asyncio
import time

import pytest
from cherenkov.core.base_scanner import BaseScanner, ScanResult
from cherenkov.core.engine import ScanEngine
from cherenkov.core.registry import ScannerRegistry


class WaitScanner(BaseScanner):
    name = "WaitScanner"

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        await asyncio.sleep(0.1)
        return ScanResult(target=target, scanner_name=self.name, status="success", findings=[])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_parallel_speedup():
    reg = ScannerRegistry()
    reg.register(WaitScanner, explicit_name="WaitScanner")
    engine = ScanEngine(reg)

    target = "http://speed-test.local"
    # The registry uses wait
    scanners = ["wait", "wait", "wait"]

    # 1. Sequential execution (simulated)
    start_seq = time.time()
    for s in scanners:
        await engine.scan_single(s, target)
    duration_seq = time.time() - start_seq

    # 2. Parallel execution
    start_par = time.time()
    await engine.scan_all(target, scanners=scanners, max_concurrent=3)
    duration_par = time.time() - start_par

    print(f"\nSequential duration: {duration_seq:.2f}s")
    print(f"Parallel duration: {duration_par:.2f}s")

    # Sequential should take ~0.3s (3 * 0.1s)
    # Parallel should take ~0.1s (1 * 0.1s)
    assert duration_seq >= 0.3
    assert duration_par < 0.3
    assert duration_par < duration_seq * 0.9
