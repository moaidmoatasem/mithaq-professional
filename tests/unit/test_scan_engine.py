import asyncio
import pytest
import time
from typing import Dict
from cherenkov.core.engine import ScanEngine
from cherenkov.core.registry import ScannerRegistry
from cherenkov.core.base_scanner import BaseScanner, ScanResult

class SlowScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        await asyncio.sleep(1.0)
        return ScanResult(target=target, scanner_name=self.name, status="success", findings=[])

class FastScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        return ScanResult(target=target, scanner_name=self.name, status="success", findings=[])

class FailScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        raise Exception("Scanner failed")

@pytest.fixture
def registry():
    reg = ScannerRegistry()
    # We'll just add our mock ones to the existing registry
    reg.register(SlowScanner)
    reg.register(FastScanner)
    reg.register(FailScanner)
    return reg

@pytest.fixture
def engine(registry):
    return ScanEngine(registry)

@pytest.mark.asyncio
async def test_scan_all_concurrency(engine, registry):
    # Register 3 different slow scanners to avoid dict key collision
    class SlowScanner1(SlowScanner): pass
    class SlowScanner2(SlowScanner): pass
    class SlowScanner3(SlowScanner): pass
    registry.register(SlowScanner1)
    registry.register(SlowScanner2)
    registry.register(SlowScanner3)
    
    scanners = ["slowscanner1", "slowscanner2", "slowscanner3"]
    
    start_time = time.time()
    results = await engine.scan_all("http://test.local", scanners=scanners, max_concurrent=3)
    duration = time.time() - start_time
    
    assert len(results) == 3
    assert duration < 2.0

@pytest.mark.asyncio
async def test_scan_all_error_handling(engine):
    results = await engine.scan_all("http://error-handling.local", scanners=["fast", "fail"])
    
    assert results["fast"].status == "success"
    assert results["fail"].status == "failed"

@pytest.mark.asyncio
async def test_scan_progress_callback(engine):
    progress_updates = []
    
    async def on_progress(scanner_name: str, result: ScanResult):
        progress_updates.append((scanner_name, result.status))
        
    await engine.scan_all("http://progress.local", scanners=["fast", "slow"], on_progress=on_progress)
    
    assert len(progress_updates) == 2
    assert ("fast", "success") in progress_updates
    assert ("slow", "success") in progress_updates

@pytest.mark.asyncio
async def test_circuit_breaker_integration(engine):
    # Trip the breaker for this target by failing 3 times (default_threshold=3 in my edit)
    # Actually, we need to fail it 3 times.
    
    target = "http://failing-target.com"
    
    # 1st fail
    await engine.scan_all(target, scanners=["fail"])
    # 2nd fail
    await engine.scan_all(target, scanners=["fail"])
    # 3rd fail
    await engine.scan_all(target, scanners=["fail"])
    
    # Now the breaker should be OPEN
    results = await engine.scan_all(target, scanners=["fast"])
    assert results["fast"].status == "circuit_open"
