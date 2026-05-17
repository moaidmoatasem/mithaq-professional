"""Scanner Registry - Auto-discovery"""

import importlib
import inspect
import pkgutil
from typing import Dict, List, Type

from .base_scanner import BaseScanner


class ScannerRegistry:
    """Auto-discovers all scanners in scanners/ directory"""

    def __init__(self, scanners_path: str = "cherenkov.scanners"):
        self.scanners_path = scanners_path
        self._registry: Dict[str, Type[BaseScanner]] = {}
        self._load_scanners()

        # Explicitly register graduated scanners (unimplemented ones stay in _load_scanners auto-discovery)
        from cherenkov.scanners.path_traversal_scanner import PathTraversalScanner
        from cherenkov.scanners.xxe_scanner import XXEScanner

        self.register(XXEScanner)
        self.register(PathTraversalScanner)

    def register(self, scanner_class: Type[BaseScanner]):
        """Manually register a scanner class"""
        scanner_name = scanner_class.__name__.replace("Scanner", "").lower()
        self._registry[scanner_name] = scanner_class

    def _load_scanners(self):
        """Auto-discover scanners using importlib"""
        package = importlib.import_module(self.scanners_path)
        for _, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if not ispkg:  # Only modules, not packages
                try:
                    module = importlib.import_module(name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            inspect.isclass(attr)
                            and issubclass(attr, BaseScanner)
                            and attr != BaseScanner
                        ):
                            scanner_name = attr.__name__.replace("Scanner", "").lower()
                            self._registry[scanner_name] = attr
                except ImportError:
                    continue  # Skip broken scanners

    def list_scanners(self) -> List[str]:
        """List all available scanners"""
        return sorted(self._registry.keys())

    def get_scanner(self, name: str) -> Type[BaseScanner]:
        """Get scanner by name"""
        if name not in self._registry:
            raise ValueError(f"Scanner '{name}' not found. Available: {self.list_scanners()}")
        return self._registry[name]

    def create_scanner(self, name: str) -> BaseScanner:
        """Instantiate scanner"""
        scanner_class = self.get_scanner(name)
        return scanner_class()
