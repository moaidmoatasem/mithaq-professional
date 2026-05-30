import { test, expect } from '@playwright/test';

test.describe('Cherenkov Sovereign Platform E2E Flow', () => {

  test('should block access, allow credential rotation, and complete a code scan', async ({ page }) => {
    // 1. Visit frontend dev port
    await page.goto('/');

    // 2. Assert credentials blocker is presented
    await expect(page.locator('text=Security Initialization Blocker')).toBeVisible();
    await expect(page.locator('text=Rotate Credentials & Unlock')).toBeVisible();

    // 3. Complete rotation
    await page.fill('input[placeholder="Minimum 8 characters..."]', 'mySecureAdministratorPassphrase2026!');
    await page.click('button:has-text("Rotate Credentials & Unlock")');

    // 4. Assert unlock transitions successfully to dashboard
    // The modal should hide, presenting the main dashboard options
    await expect(page.locator('text=Static Analysis Swarms')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Autonomic Health Status')).toBeVisible();

    // 5. Assert health diagnostics rendering
    await expect(page.locator('text=Registry Database')).toBeVisible();
    await expect(page.locator('text=LLM Inference Host')).toBeVisible();

    // 6. Perform source code scan
    const insecureCode = 'db.execute("SELECT * FROM keys WHERE name = \'" + input + "\'");';
    await page.fill('textarea', insecureCode);

    // Trigger the scan
    await page.click('button:has-text("Execute Agent Audit")');

    // 7. Assert reports render findings
    await expect(page.locator('text=Audit Report Findings')).toBeVisible({ timeout: 10000 });

    // Assert metrics generated in panel
    await expect(page.locator('text=Throughput')).toBeVisible();
    await expect(page.locator('text=Total Tokens')).toBeVisible();
  });
});
