# Save as scripts/opencode_tasks.sh in the repo
# Usage: bash scripts/opencode_tasks.sh graduate cors_scanner

SCANNER=$1
if [ -z "$SCANNER" ]; then
  echo "Usage: $0 <scanner_name>"
  exit 1
fi

opencode "
Graduate packages/cherenkov/autonomous_generated/scanners/${SCANNER}.py

Steps:
1. Read the file
2. Refactor to inherit BaseScanner from packages/cherenkov/core/base_scanner.py
3. Implement: async def scan(self, target: str, timeout: float = 10.0) -> ScanResult
4. Write tests/unit/test_${SCANNER}.py with positive and negative cases
5. Add to packages/cherenkov/core/registry.py
6. Run: export PYTHONPATH=\$PYTHONPATH:\$(pwd)/packages && pytest tests/unit/test_${SCANNER}.py -v
7. Run: bandit packages/cherenkov/scanners/${SCANNER}.py && ruff check packages/cherenkov/scanners/${SCANNER}.py
8. If all pass: move file to packages/cherenkov/scanners/
9. git checkout -b feat/graduate-${SCANNER}
10. git add -A && git commit -m 'feat(scanners): graduate ${SCANNER} to BaseScanner contract'
11. gh pr create --title 'feat(scanners): graduate ${SCANNER}' --body 'Closes #A12'
"
