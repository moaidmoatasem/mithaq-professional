import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('should display the main hub dashboard', async ({ page }) => {
    // Check main panels
    await expect(page.locator('h2', { hasText: 'C2 Hub Dashboard' })).toBeVisible();
    
    // Check buttons
    await expect(page.locator('button', { hasText: 'INITIATE NEW SCAN' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'REBOOT_TOPOLOGY' })).toBeVisible();
  });

  test('should open New Scan form modal', async ({ page }) => {
    // Click New Scan button
    await page.locator('button', { hasText: 'INITIATE NEW SCAN' }).click();
    
    // Check if modal appears
    await expect(page.locator('h3', { hasText: 'Configure New Scan' })).toBeVisible();
    
    // Ensure form fields exist
    await expect(page.locator('input[type="text"]').first()).toHaveValue('https://target.example.com');
    await expect(page.locator('select').first()).toHaveValue('web');
    
    // Submit form (without backend running, it should show error)
    await page.locator('button', { hasText: 'LAUNCH SCAN' }).click();
    
    // Assert error state (wait a bit for network rejection)
    await expect(page.locator('text=Failed to fetch').or(page.locator('text=Failed to start scan'))).toBeVisible({ timeout: 5000 });
    
    // Cancel modal
    await page.locator('button', { hasText: 'CANCEL' }).click();
    await expect(page.locator('h3', { hasText: 'Configure New Scan' })).not.toBeVisible();
  });

  test('should display Ablation Meter', async ({ page }) => {
    await expect(page.locator('text=Ablation_Meter')).toBeVisible();
    await expect(page.locator('text=Drop_Rate')).toBeVisible();
    // These only show up on hover initially because they are in the Tooltip but playwright's text locator looks anywhere
    await expect(page.locator('text=Total Drops')).toBeVisible();
    await expect(page.locator('text=Total Attempts')).toBeVisible();

    // Since the API is not active, it should be offline
    await expect(page.locator('text=BACKEND OFFLINE')).toBeVisible();
  });

  test('should display Queue Depth Sparkline', async ({ page }) => {
    await expect(page.locator('text=Redis_Queue')).toBeVisible();
    await expect(page.locator('text=Jobs:')).toBeVisible();
  });

  test('should display Threat Intel Panel traces', async ({ page }) => {
    await expect(page.locator('text=Unauthenticated RCE')).toBeVisible();
    await expect(page.locator('text=SSRF in Image Relay')).toBeVisible();
    
    // Expand a threat
    await page.locator('text=Unauthenticated RCE').first().click();
    
    // Check for expanded content
    await expect(page.getByRole('button', { name: 'VIEW PROOF' }).or(page.getByText('VIEW PROOF')).first()).toBeVisible({ timeout: 5000 });

    // Click VIEW PROOF
    await page.getByText('VIEW PROOF').first().click();

    // Check proof drawer
    await expect(page.locator('text=Mem_Redact_Buffers')).toBeVisible();
    await expect(page.getByRole('button', { name: 'EXPORT TRACE (.JSON)' }).or(page.getByText('EXPORT TRACE (.JSON)')).first()).toBeVisible();
    await expect(page.getByRole('button', { name: 'CLOSE' }).or(page.getByText('CLOSE')).first()).toBeVisible();
  });

  test('should display Node Status Rows', async ({ page }) => {
    const expectedNodes = ['TENSOR', 'KINETIC', 'AEGIS', 'LATTICE', 'TOKAMAK'];
    
    for (const node of expectedNodes) {
      await expect(page.locator('span', { hasText: node }).first()).toBeVisible();
    }
  });

});
