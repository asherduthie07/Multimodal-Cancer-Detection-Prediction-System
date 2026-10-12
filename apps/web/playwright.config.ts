import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: { baseURL: 'http://localhost:4200', browserName: 'chromium', channel: 'chrome' },
  reporter: 'list',
});
