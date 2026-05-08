import unittest
from unittest.mock import patch

from cherenkov.core.base_scanner import BaseScanner, ScanResult
from cherenkov.core.registry import ScannerRegistry


class MockScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        return ScanResult(target=target, scanner_name="mock")


class TestScannerRegistry(unittest.TestCase):
    def setUp(self):
        # We patch load_scanners to avoid actual file system scanning during most tests
        with patch.object(ScannerRegistry, "_load_scanners"):
            self.registry = ScannerRegistry()
            self.registry._registry = {"mock": MockScanner}

    def test_get_scanner_success(self):
        """Test retrieving a scanner that exists in the registry"""
        scanner_class = self.registry.get_scanner("mock")
        self.assertEqual(scanner_class, MockScanner)

    def test_get_scanner_not_found(self):
        """Test that get_scanner raises ValueError for unknown scanners"""
        with self.assertRaises(ValueError) as cm:
            self.registry.get_scanner("nonexistent")

        error_msg = str(cm.exception)
        self.assertIn("Scanner 'nonexistent' not found", error_msg)
        self.assertIn("Available: ['mock']", error_msg)

    def test_list_scanners(self):
        """Test listing available scanners"""
        self.registry._registry["alpha"] = MockScanner
        self.assertEqual(self.registry.list_scanners(), ["alpha", "mock"])

    def test_create_scanner(self):
        """Test instantiation of a scanner"""
        scanner = self.registry.create_scanner("mock")
        self.assertIsInstance(scanner, MockScanner)
        self.assertEqual(scanner.name, "MockScanner")


if __name__ == "__main__":
    unittest.main()
