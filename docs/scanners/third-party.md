# Third-Party Wrappers

CHERENKOV supports wrapping third-party scanning tools as CHERENKOV scanners. This allows you to integrate existing tools into the Trident workflow.

## How It Works

1. Create a wrapper class that inherits from `BaseScanner`
2. The wrapper runs the third-party tool via subprocess or API
3. Output is parsed and converted to `ScanResult` format
4. Results pass through the Validation Gate like native scanners

## Example

```python
class NucleiWrapper(BaseScanner):
    name = "nuclei"
    description = "Nuclei template-based scanner"
    
    async def scan(self, target: str) -> ScanResult:
        result = await run_subprocess(["nuclei", "-u", target, "-json"])
        return parse_nuclei_output(result)
```

## Supported Wrappers

- Nuclei
- Zapier / ZAP
- Custom tools via CLI or REST API
