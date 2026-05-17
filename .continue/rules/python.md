## Python Rules

- Canonical path: packages/cherenkov/ (NOT src/)
- Imports: from cherenkov.X import Y, never from src.cherenkov
- All scanners must inherit BaseScanner from cherenkov.core.base_scanner
- async scan(target: str, timeout: float = 10.0) -> ScanResult contract
- MEISSNER rule: zero outbound calls beyond the scan target URL
- ABLATION: pipe LLM payloads through cherenkov.core.ablation before sending
- TOKAMAK: all PoC output must be SHA-256 signed (trace_hash)
- Shred: temp file cleanup = overwrite + JSON receipt, never bare os.remove()
- Pre-commit: ruff format packages/ && ruff check packages/ --ignore W,S,B
