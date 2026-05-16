# Writing a Scanner

Scanners are Python classes that inherit from `BaseScanner`. They are auto-discovered and registered by the `ScannerRegistry`.

## Basic Template

```python
from cherenkov.core.base_scanner import BaseScanner
from cherenkov.core.models import ScanResult

class MyScanner(BaseScanner):
    name = "my-scanner"
    description = "Detects XYZ vulnerabilities"
    
    async def scan(self, target: str) -> ScanResult:
        # Your scanning logic here
        return ScanResult(
            scanner=self.name,
            target=target,
            findings=[...]
        )
```

## Registration

Place your scanner file in the `scanners/` directory. It will be auto-discovered on next startup.

## Requirements

- Must implement `async def scan(self, target: str) -> ScanResult`
- Must set `name` and `description` class attributes
- Must return a `ScanResult` with typed findings
- Should handle errors gracefully and return partial results on failure
