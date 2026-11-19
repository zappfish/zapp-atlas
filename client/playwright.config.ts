import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

import { defineConfig, devices } from '@playwright/test';

// The browser tests run against the real server: the FastAPI app, serving the
// built client, on a database that exists only for this run. Development
// sign-in is on, and the seed gives that identity a research group with a
// stocked fish tank and chemical cabinet, so a test can sign in and find
// records straight away.
//
// The server's reference data comes from a bundle it may not have on a CI
// machine, so the run gets its own: a zfin.db built from the same miniature
// ZFIN files the server tests use (server/tests/zfin_fixture). The fish tests
// know those lines; the ontology files are left out, as no test reads them.
//
// Run `npm run e2e`, which builds the client first: the server serves
// client/dist, not the source.

const PORT = 8765;
const repo = path.resolve(import.meta.dirname, '..');

// Playwright loads this file again in each worker. The directory is made once
// and handed down through the environment, so they all name the same one.
const dataDir = (process.env.ZAPP_E2E_DATA ??= mkdtempSync(
  path.join(tmpdir(), 'zapp-e2e-'),
));

const extdataDir = path.join(dataDir, 'extdata');
if (!existsSync(path.join(extdataDir, 'zfin.db'))) {
  mkdirSync(extdataDir, { recursive: true });
  execFileSync(
    'uv',
    [
      'run',
      '--quiet',
      '--script',
      path.join(repo, 'extdata', 'scripts', 'zfin_db.py'),
      path.join(extdataDir, 'zfin.db'),
      path.join(repo, 'server', 'tests', 'zfin_fixture'),
      '--zfin-date',
      'fixture',
    ],
    { stdio: 'inherit' },
  );
}

export default defineConfig({
  testDir: 'e2e',
  forbidOnly: !!process.env.CI,
  reporter: 'list',
  use: { baseURL: `http://localhost:${PORT}` },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `uv run uvicorn zapp_atlas.main:app --port ${PORT}`,
    cwd: path.resolve(import.meta.dirname, '../server'),
    url: `http://localhost:${PORT}/health`,
    reuseExistingServer: false,
    env: {
      ZAPP_DB_PATH: path.join(dataDir, 'zapp.db'),
      ZAPP_UPLOAD_DIR: path.join(dataDir, 'uploads'),
      ZAPP_EXTDATA_DIR: extdataDir,
      ZAPP_DEV_AUTH: 'true',
      // A developer's server/.env may point at a Vite dev server.
      ZAPP_VITE_DEV_SERVER: '',
    },
  },
});
