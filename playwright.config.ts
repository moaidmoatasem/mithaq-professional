import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'python3 packages/cherenkov/meissner/server.py',
      port: 8080,
      reuseExistingServer: true,
      timeout: 10000,
    },
    {
      command: 'npm run dev',
      port: 8000,
      reuseExistingServer: true,
      timeout: 10000,
    }
  ]
});

