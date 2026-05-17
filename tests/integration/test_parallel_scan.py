import asyncio
import pytest
import time
from cherenkov.core.engine import ScanEngine
from cherenkov.core.registry import ScannerRegistry
from cherenkov.core.base_scanner import BaseScanner, ScanResult

class WaitScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        # Wait for 2 seconds to simulate work
        await asyncio.sleep(2.0)
        return ScanResult(target=target, scanner_name=self.name, status="success", findings=[])

@pytest.mark.integration
@pytest.mark.asyncio
async def test_parallel_speedup():
    reg = ScannerRegistry()
    reg.register(WaitScanner)
    engine = ScanEngine(reg)
    
    target = "http://speed-test.local"
    # The registry typically uses the class name if __init__ doesn't override it,
    # but origin/main had 'wait'. Let's use 'WaitScanner' which is safer.
    scanners = ["WaitScanner", "WaitScanner", "WaitScanner"]
    
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
    
    # Sequential should take ~6s (3 * 2s)
    # Parallel should take ~2s (1 * 2s)
    assert duration_seq >= 5.5
    assert duration_par < 3.0
    assert duration_par < duration_seq / 2
