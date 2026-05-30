import { defineConfig, defaultExclude } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: [],
    exclude: [...defaultExclude, 'tests/e2e/**', '**/*.spec.ts', 'packages/cherenkov/web/**'],
  },
});
