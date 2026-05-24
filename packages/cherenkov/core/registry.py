"""Scanner Registry - Auto-discovery"""

import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Type

from .base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class ScannerRegistry:
    """Auto-discovers all scanners in scanners/ directory"""

    def __init__(self, scanners_path: str = "cherenkov.scanners"):
        self.scanners_path = scanners_path
        self._registry: Dict[str, Type[BaseScanner]] = {}
        self.discover_scanners()

    def register(self, scanner_class: Type[BaseScanner], explicit_name: str = None):
        """Manually register a scanner class"""
        if explicit_name:
            scanner_name = explicit_name
        else:
            scanner_name = scanner_class.__name__.replace("Scanner", "").lower()
        self._registry[scanner_name] = scanner_class

    def discover_scanners(self):
        """Auto-discover scanners using importlib and pkgutil"""
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
                            and not inspect.isabstract(attr)
                            and attr != BaseScanner
                        ):
                            scanner_name = attr.__name__.replace("Scanner", "").lower()
                            self.register(attr, scanner_name)
                except ImportError:
                    logger.error(f"Failed to import module {name}", exc_info=True)

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
