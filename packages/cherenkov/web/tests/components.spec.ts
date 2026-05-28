import { test, expect } from '@playwright/test';

test.describe('Auth Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.sessionStorage.removeItem('cherenkov_token');
    });
    await page.route('**/api/v1/auth/token', async route => {
      const body = JSON.parse(route.request().postData() || '{}');
      if (body.username === 'admin' && body.password === 'admin') {
        await route.fulfill({ status: 200, json: { access_token: 'test-token', token_type: 'bearer' } });
      } else {
        await route.fulfill({ status: 401, json: { detail: 'Incorrect username or password' } });
      }
    });
  });

  test('should show login page when not authenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=CHERENKOV')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('input[type="text"]')).toBeVisible();
  });

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'wrong');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Incorrect')).toBeVisible({ timeout: 5000 });
  });
});

const DASHBOARD_MOCKS = {
  '**/api/v1/health': { status: 'healthy', nodes: {}, queue: { scan_jobs_pending: 0 } },
  '**/api/v1/ablation/stats': { session_stats: { attempts: 0, drops: 0, drop_rate: 0, alert_active: false } },
  '**/api/v1/findings/pending': [] as any[],
  '**/api/v1/scans/history': [],
  '**/api/v1/models/recommend': { models: [] },
};

test.describe('AssistantWidget', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.sessionStorage.setItem('cherenkov_token', 'dummy-token');
    });
    for (const [url, json] of Object.entries(DASHBOARD_MOCKS)) {
      await page.route(url, async route => {
        await route.fulfill({ status: 200, json });
      });
    }
    await page.goto('/');
    // Wait for dashboard to render (token should skip login)
    await expect(page.locator('text=CHERENKOV').first()).toBeVisible({ timeout: 15000 });
  });

  test('should open assistant widget on FAB click', async ({ page }) => {
    const fab = page.locator('button:has(svg.lucide-message-square)');
    await expect(fab).toBeVisible({ timeout: 10000 });
    await fab.click();
    await expect(page.locator('text=AI Security Assistant')).toBeVisible();
  });

  test('should send user message and show AI response', async ({ page }) => {
    await page.route('**/api/v1/assistant/advice', async route => {
      await route.fulfill({ status: 200, json: { advice: 'Ensure all endpoints are properly authenticated.' } });
    });

    const fab = page.locator('button:has(svg.lucide-message-square)');
    await fab.click();
    await page.waitForTimeout(500);
    const input = page.locator('input[placeholder*="Ask about"]');
    await expect(input).toBeVisible({ timeout: 5000 });
    await input.fill('How to secure API?');
    await page.click('button:has(svg.lucide-send)');
    await expect(page.locator('text=Ensure all endpoints')).toBeVisible({ timeout: 10000 });
  });

  test('should pass scan findings as context', async ({ page }) => {
    let requestBody: any = null;
    await page.route('**/api/v1/assistant/advice', async route => {
      requestBody = JSON.parse(route.request().postData() || '{}');
      await route.fulfill({ status: 200, json: { advice: 'Scan findings received.' } });
    });

    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('cherenkov:scan_complete', {
        detail: {
          scan_id: 'test-123',
          target: 'https://example.com',
          vulnerabilities: [{ title: 'XSS', severity: 'high', cwe: 'CWE-79', description: 'Cross-site scripting' }],
          count: 1,
        },
      }));
    });

    const fab = page.locator('button:has(svg.lucide-message-square)');
    await fab.click();
    await page.waitForTimeout(500);
    const input = page.locator('input[placeholder*="Ask about"]');
    await expect(input).toBeVisible({ timeout: 5000 });
    await input.fill('Analyze findings');
    await page.click('button:has(svg.lucide-send)');
    await expect(page.locator('text=Scan findings received')).toBeVisible({ timeout: 10000 });

    expect(requestBody).not.toBeNull();
    expect(requestBody.findings.length).toBe(1);
    expect(requestBody.findings[0].cwe).toBe('CWE-79');
  });
});

test.describe('PendingApprovalsPanel', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.sessionStorage.setItem('cherenkov_token', 'dummy-token');
    });
    for (const [url, json] of Object.entries(DASHBOARD_MOCKS)) {
      await page.route(url, async route => {
        await route.fulfill({ status: 200, json });
      });
    }
  });

  test('should display pending approvals', async ({ page }) => {
    await page.route('**/api/v1/findings/pending', async route => {
      await route.fulfill({
        status: 200,
        json: [
          { finding_id: 'f1', severity: 'CRITICAL', scanner: 'xss', title: 'XSS Vulnerability', status: 'pending' },
          { finding_id: 'f2', severity: 'HIGH', scanner: 'csrf', title: 'CSRF Token Missing', status: 'pending' },
        ],
      });
    });

    await page.goto('/');
    await expect(page.locator('text=XSS Vulnerability')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=CSRF Token Missing')).toBeVisible();
  });

  test('should approve a finding', async ({ page }) => {
    let findingsPending = true;
    await page.route('**/api/v1/findings/pending', async route => {
      await route.fulfill({
        status: 200,
        json: findingsPending ? [
          { finding_id: 'f1', severity: 'CRITICAL', scanner: 'xss', title: 'XSS Vulnerability', status: 'pending' },
        ] : [],
      });
    });
    let approvedId = '';
    await page.route('**/api/v1/findings/f1/approve', async route => {
      approvedId = 'f1';
      findingsPending = false;
      await route.fulfill({ status: 200, json: { status: 'success' } });
    });

    await page.goto('/');
    await expect(page.locator('text=XSS Vulnerability')).toBeVisible({ timeout: 15000 });
    const approveBtn = page.locator('button:has(svg.lucide-check)').first();
    await expect(approveBtn).toBeVisible({ timeout: 5000 });
    await approveBtn.click();
    await expect(page.locator('text=No pending approvals')).toBeVisible({ timeout: 10000 });
    expect(approvedId).toBe('f1');
  });
});
