import { test, expect } from '@playwright/test';

test.describe('Dashboard API Mocks', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the Health API
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 200,
        json: {
          status: 'operational',
          meissner: { state: 'CLOSED' },
          nodes: {
            tensor: { status: 'ready', model: 'MOCK LLAMA' },
            kinetic: { status: 'busy', model: 'MOCK QWEN', ram_gb: 3.1 },
            aegis: { status: 'offline' },
            lattice: { status: 'ready', vector_count: 5000 },
            tokamak: { status: 'ready', active_containers: 2 }
          },
          queue: { scan_jobs_pending: 12 }
        }
      });
    });

    // Mock Ablation Stats
    await page.route('**/api/v1/ablation/stats', async route => {
      await route.fulfill({
        status: 200,
        json: {
          session_stats: {
            attempts: 500,
            drops: 50,
            drop_rate: 0.1,
            alert_active: false
          },
          drop_reasons: {
            pii_residual: 50
          }
        }
      });
    });

    await page.goto('/');
  });

  test('should display mocked data correctly', async ({ page }) => {
    // Wait for the mock to populate data
    await expect(page.locator('text=BACKEND OFFLINE')).not.toBeVisible();

    // Check Node models and status
    await expect(page.locator('span', { hasText: 'MOCK LLAMA' }).first()).toBeVisible();
    await expect(page.locator('span', { hasText: 'MOCK QWEN' }).first()).toBeVisible();
    await expect(page.locator('span', { hasText: '3.1GB' }).first()).toBeVisible();
    await expect(page.locator('span', { hasText: '5000 Vectors' }).first()).toBeVisible();
    await expect(page.locator('span', { hasText: '2 Contain.' }).first()).toBeVisible();

    // Check Ablation Stats
    await expect(page.locator('text=10.0%')).toBeVisible();
    await expect(page.getByText('50', { exact: true })).toBeVisible(); // Drops value
    await expect(page.getByText('500', { exact: true })).toBeVisible(); // Attempts value
    
    // The reason is shown on hover, but we just check if it's there
    // pii residual should be capitalized
    await expect(page.locator('text=pii residual').first()).toBeVisible({ timeout: 5000 });

    // Check Queue Depth
    await expect(page.locator('text=12 pending')).toBeVisible();
  });
});
