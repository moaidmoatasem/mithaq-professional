# Task: Issue #236 — Scanner registry auto-discover all BaseScanner subclasses

**Branch:** `feat/236-scanner-registry`
**Labels:** `priority:high, feature, phase-2, area:scanner`
**Milestone:** v1.1.0
**PR must contain:** `Closes #236`

## Context

Scanners are currently manually registered in `packages/cherenkov/core/registry.py`.
This creates maintenance burden and makes it easy to forget registering new scanners.
The registry should auto-discover all `BaseScanner` subclasses via `importlib` or
`__init_subclass__`.

## Context files

```
packages/cherenkov/core/registry.py        ← current manual registry
packages/cherenkov/core/base_scanner.py    ← BaseScanner base class
packages/cherenkov/scanners/               ← production scanners to discover
packages/cherenkov/scanners/__init__.py    ← may need updating for imports
```

## What to do

1. **Choose auto-discovery strategy** (prefer `importlib` + `pkgutil`):

   ```python
   # packages/cherenkov/core/registry.py
   import importlib
   import pkgutil
   from pathlib import Path
   from cherenkov.core.base_scanner import BaseScanner

   class ScannerRegistry:
       def __init__(self):
           self._scanners: dict[str, BaseScanner] = {}

       def register(self, scanner: BaseScanner) -> None:
           self._scanners[scanner.name] = scanner

       def get(self, name: str) -> BaseScanner | None:
           return self._scanners.get(name)

       def all(self) -> list[BaseScanner]:
           return list(self._scanners.values())

       def discover(self, package_name: str = "cherenkov.scanners") -> None:
           """Auto-discover and register all BaseScanner subclasses in a package."""
           package = importlib.import_module(package_name)
           package_path = Path(package.__file__).parent

           for _, module_name, _ in pkgutil.walk_packages(
               [str(package_path)], prefix=f"{package_name}."
           ):
               try:
                   module = importlib.import_module(module_name)
                   for attr_name in dir(module):
                       attr = getattr(module, attr_name)
                       if (
                           isinstance(attr, type)
                           and issubclass(attr, BaseScanner)
                           and attr is not BaseScanner
                       ):
                           instance = attr()
                           self.register(instance)
               except Exception:
                   pass  # Skip modules that fail to import

   # Singleton
   registry = ScannerRegistry()
   ```

2. **Remove manual registration calls** — replace with `registry.discover()`

3. **Add `discover()` call** at application startup (in `api/main.py` lifespan or import-time)

4. **Write tests**:
   ```python
   # tests/unit/test_scanner_registry.py
   def test_registry_discover_finds_scanners():
       from cherenkov.core.registry import ScannerRegistry
       reg = ScannerRegistry()
       reg.discover("cherenkov.scanners")
       assert len(reg.all()) > 0

   def test_registry_no_duplicate_names():
       from cherenkov.core.registry import ScannerRegistry
       reg = ScannerRegistry()
       reg.discover("cherenkov.scanners")
       names = [s.name for s in reg.all()]
       assert len(names) == len(set(names))
   ```

## Files to modify

- `packages/cherenkov/core/registry.py` — rewrite with auto-discovery
- `packages/cherenkov/api/main.py` — call `registry.discover()` at startup
- `tests/unit/test_scanner_registry.py` — new test file

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_scanner_registry.py -v
python -c "from cherenkov.core.registry import registry; registry.discover(); print(f'Discovered {len(registry.all())} scanners'); [print(f'  - {s.name}') for s in registry.all()]"
```
