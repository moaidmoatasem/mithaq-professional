import asyncio
from cherenkov.core.base_scanner import BaseScanner, ScanResult
from cherenkov.core.registry import ScannerRegistry
from cherenkov.core.engine import ScanEngine


class MockScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        return ScanResult(target=target, scanner_name="mock")


def test_engine_scan_all_returns_results():
    registry = ScannerRegistry()
    registry._registry = {"mock": MockScanner}
    engine = ScanEngine(registry)
    results = asyncio.run(engine.scan_all("https://example.com"))
    assert "mock" in results
    assert results["mock"].target == "https://example.com"


def test_engine_scan_single_returns_result():
    registry = ScannerRegistry()
    registry._registry = {"mock": MockScanner}
    engine = ScanEngine(registry)
    result = asyncio.run(engine.scan_single("mock", "https://example.com"))
    assert result.scanner_name == "mock"
    assert result.status == "completed"
