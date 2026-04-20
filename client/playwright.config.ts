import { defineConfig, devices } from '@playwright/test';

const apiPort = process.env.API_PORT || '8000';
const devPort = process.env.DEV_PORT || '5173';

export default defineConfig({
  testDir: './tests',
  // Curation specs drive the real frogpot phenotype picker, which
  // pulls down multi-MB ZFA/ZP ontology JSON — too slow for the smoke
  // suite. They're gated behind their own ``just curate`` recipe.
  testIgnore: process.env.INCLUDE_CURATIONS ? [] : ['**/curations/**'],
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: `http://localhost:${devPort}`,
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'cd ../server && PYTHONPATH=.. uv run uvicorn server.api.main:app --port ' + apiPort,
      url: `http://localhost:${apiPort}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: `npm run dev -- --port ${devPort}`,
      url: `http://localhost:${devPort}`,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
  ],
});
