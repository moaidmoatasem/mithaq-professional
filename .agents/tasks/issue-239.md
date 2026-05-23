# Task: Issue #239 — Phase 2 CI test matrix — ensure 146+ tests pass

**Branch:** `test/239-ci-matrix`
**Labels:** `priority:high, test, phase-2, area:infra`
**Milestone:** v1.1.0
**PR must contain:** `Closes #239`

## Context

The CI test suite needs to reliably pass with 146+ tests before Phase 2 can close.
Any broken tests need to be fixed, flaky tests stabilized, and the test matrix
verified across the expected markers (unit, integration, ai_generated).

## What to do

1. **Run the full unit test suite** and capture failures:
   ```bash
   pytest -m "not (integration or ai_generated)" --tb=short -q 2>&1 | tee test_results.txt
   ```

2. **Categorize failures** into:
   - **Import errors** — missing modules, wrong import paths
   - **Assertion errors** — logic changed but tests not updated
   - **Flaky tests** — timing, network, or ordering issues
   - **Stale tests** — reference removed/renamed code

3. **Fix each failure**:
   - Update imports to match current module locations
   - Update assertions to match current behavior
   - Add `@pytest.mark.flaky` or stabilize timing-sensitive tests
   - Delete tests for code that no longer exists

4. **Verify test count**:
   ```bash
   pytest -m "not (integration or ai_generated)" --co -q | tail -1
   # Expected: 146+ tests collected
   ```

5. **Update CI workflow** if needed (`.github/workflows/ci.yml`):
   - Ensure pytest runs with correct markers
   - Ensure Python version matches (3.11)

## Files to modify

- `tests/` — fix broken tests
- `.github/workflows/ci.yml` — verify/update test step
- Various `packages/` files if tests reveal import breakage

## Verify

```bash
# Full suite must pass
pytest -m "not (integration or ai_generated)" --tb=short -q
# Expected: 146+ passed, 0 failed

# Lint
ruff format packages/ && ruff check packages/ --ignore W,S,B

# Count
pytest -m "not (integration or ai_generated)" --co -q | tail -1
```
