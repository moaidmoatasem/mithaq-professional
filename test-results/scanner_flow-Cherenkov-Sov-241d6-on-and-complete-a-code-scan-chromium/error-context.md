# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: scanner_flow.spec.ts >> Cherenkov Sovereign Platform E2E Flow >> should block access, allow credential rotation, and complete a code scan
- Location: tests/e2e/scanner_flow.spec.ts:5:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Security Initialization Blocker')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=Security Initialization Blocker')

```

```yaml
- img
- heading "Sovereign Access" [level=1]
- paragraph: CHERENKOV // SECURITY OPERATIONS CENTER
- text: Operator ID
- textbox "admin"
- text: Secure Key
- textbox "••••••••"
- button "INITIALIZE SESSION"
- paragraph: MEISSNER AIR-GAP PROTOCOL ENFORCED // NO EXTERNAL EGRESS
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Cherenkov Sovereign Platform E2E Flow', () => {
  4  |   
  5  |   test('should block access, allow credential rotation, and complete a code scan', async ({ page }) => {
  6  |     // 1. Visit frontend dev port
  7  |     await page.goto('/');
  8  | 
  9  |     // 2. Assert credentials blocker is presented
> 10 |     await expect(page.locator('text=Security Initialization Blocker')).toBeVisible();
     |                                                                        ^ Error: expect(locator).toBeVisible() failed
  11 |     await expect(page.locator('text=Rotate Credentials & Unlock')).toBeVisible();
  12 | 
  13 |     // 3. Complete rotation
  14 |     await page.fill('input[placeholder="Minimum 8 characters..."]', 'mySecureAdministratorPassphrase2026!');
  15 |     await page.click('button:has-text("Rotate Credentials & Unlock")');
  16 | 
  17 |     // 4. Assert unlock transitions successfully to dashboard
  18 |     // The modal should hide, presenting the main dashboard options
  19 |     await expect(page.locator('text=Static Analysis Swarms')).toBeVisible({ timeout: 5000 });
  20 |     await expect(page.locator('text=Autonomic Health Status')).toBeVisible();
  21 | 
  22 |     // 5. Assert health diagnostics rendering
  23 |     await expect(page.locator('text=Registry Database')).toBeVisible();
  24 |     await expect(page.locator('text=LLM Inference Host')).toBeVisible();
  25 | 
  26 |     // 6. Perform source code scan
  27 |     const insecureCode = 'db.execute("SELECT * FROM keys WHERE name = \'" + input + "\'");';
  28 |     await page.fill('textarea', insecureCode);
  29 | 
  30 |     // Trigger the scan
  31 |     await page.click('button:has-text("Execute Agent Audit")');
  32 | 
  33 |     // 7. Assert reports render findings
  34 |     await expect(page.locator('text=Audit Report Findings')).toBeVisible({ timeout: 10000 });
  35 |     
  36 |     // Assert metrics generated in panel
  37 |     await expect(page.locator('text=Throughput')).toBeVisible();
  38 |     await expect(page.locator('text=Total Tokens')).toBeVisible();
  39 |   });
  40 | });
  41 | 
```