import { test, expect } from '@playwright/test';

test.describe('Dashboard UI Visual Regression Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Add stable token
    await page.addInitScript(() => {
      window.sessionStorage.setItem('cherenkov_token', 'dummy-token');
    });

    // Mock API requests to be fully static and predictable for visual comparisons
    await page.route('**/api/v1/findings/pending', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        json: [
          {
            id: 'find-1',
            severity: 'critical',
            title: 'SQL Injection in /api/v1/search',
            description: 'SQL injection vulnerabity in query parameter parsing',
            target: 'https://target.example.com',
            timestamp: '2026-05-28T23:30:00Z',
            status: 'pending'
          },
          {
            id: 'find-2',
            severity: 'high',
            title: 'Stored XSS in Comment Panel',
            description: 'Unsanitized input allows stored cross-site scripting',
            target: 'https://target.example.com',
            timestamp: '2026-05-28T23:31:00Z',
            status: 'pending'
          }
        ]
      });
    });

    // Mock static model topology list

    // Mock additional endpoints that cause ECONNREFUSED
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({ status: 200, json: { status: 'healthy', nodes: {}, queue: { scan_jobs_pending: 0 } } });
    });
    await page.route('**/api/v1/ablation/stats', async route => {
      await route.fulfill({ status: 200, json: { session_stats: { attempts: 0, drops: 0, drop_rate: 0, alert_active: false } } });
    });
    await page.route('**/api/v1/scans/history', async route => {
      await route.fulfill({ status: 200, json: [] });
    });
    await page.route('**/api/v1/models/recommend', async route => {
      await route.fulfill({ status: 200, json: { models: [] } });
    });

    await page.route('**/api/v1/models/specs', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        json: {
          detected_ram: '64GB',
          detected_vram: '24GB',
          cpu_threads: 16,
          gpu_count: 1
        }
      });
    });

    // Navigate to dashboard
    await page.goto('/');

    // Wait for the mocked findings element to be fully mounted and visible to ensure stable height
    await page.locator('text=SQL Injection in /api/v1/search').first().waitFor({ state: 'visible', timeout: 5000 });
  });

  test('should match the full dashboard screenshot', async ({ page }) => {
    // Hide dynamic text elements like system time or random logs to make it fully stable if any
    await page.evaluate(() => {
      const timeElements = document.querySelectorAll('.system-time, .dynamic-timestamp');
      timeElements.forEach(el => {
        if (el) (el as HTMLElement).style.visibility = 'hidden';
      });
    });

    // Take screenshot of the entire page and compare
    await expect(page).toHaveScreenshot('full-dashboard.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.05
    });
  });

  test('should match the Configure New Scan modal screenshot', async ({ page }) => {
    // Click New Scan button
    await page.locator('button', { hasText: 'INITIATE NEW SCAN' }).click();

    // Check if modal appears
    const modal = page.locator('h3', { hasText: 'Configure New Scan' }).locator('xpath=..');
    await expect(modal).toBeVisible();

    // Verify modal dialog visually
    await expect(modal).toHaveScreenshot('configure-new-scan-modal.png', {
      maxDiffPixelRatio: 0.05
    });
  });

  test('should match the Ablation Meter and Sparklines visual states', async ({ page }) => {
    // Assert visual status of panels specifically
    const ablationMeter = page.locator('text=Ablation_Meter').locator('xpath=../..');
    await expect(ablationMeter).toHaveScreenshot('ablation-meter.png', {
      maxDiffPixelRatio: 0.05
    });

    const redisQueue = page.locator('text=Redis_Queue').locator('xpath=../..');
    await expect(redisQueue).toHaveScreenshot('redis-queue.png', {
      maxDiffPixelRatio: 0.05
    });
  });
});
