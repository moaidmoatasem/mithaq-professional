import pytest
from unittest.mock import patch

from cherenkov.autonomous_generated.scanners.pathtraversalscanner import PathTraversalScanner
from cherenkov.core.base_scanner import Severity

@pytest.mark.asyncio
async def test_pathtraversalscanner_safe():
    scanner = PathTraversalScanner()
    with patch("os.scandir") as mock_scandir:
        mock_scandir.return_value = []
        result = await scanner.scan("/safe/target")
        assert result.scanner_name == "PathTraversalScanner"
        assert result.target == "/safe/target"
        assert len(result.findings) == 0

@pytest.mark.asyncio
async def test_pathtraversalscanner_unsafe():
    scanner = PathTraversalScanner()

    with patch("cherenkov.autonomous_generated.scanners.pathtraversalscanner.PathTraversalScanner._scan_path") as mock_scan_path:
        mock_scan_path.return_value = {
            "safe": False,
            "unsafe_paths": ["/safe/target/../../../etc/passwd"]
        }

        result = await scanner.scan("/safe/target")
        assert result.scanner_name == "PathTraversalScanner"
        assert result.target == "/safe/target"
        assert len(result.findings) == 1
        assert result.findings[0].severity == Severity.HIGH
        assert result.findings[0].description == "Unsafe path access detected: /safe/target/../../../etc/passwd"
