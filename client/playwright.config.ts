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
// machine, so the run gets its own, built from the fixtures the server tests
// use: a zfin.db from the miniature ZFIN files (server/tests/zfin_fixture),
// whose lines the fish tests know, and a labels.db of the few terms the tests
// name (server/tests/labels_fixture), without which the server stores no
// term. The ontology files the phenotype picker reads are left out, as no
// test opens it.
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

/** Run one of the bundle's own builders, as the real bundle is built. */
const build = (script: string, output: string, ...rest: string[]) =>
  execFileSync(
    'uv',
    [
      'run',
      '--quiet',
      '--script',
      path.join(repo, 'extdata', 'scripts', script),
      output,
      ...rest,
    ],
    { stdio: 'inherit' },
  );

const extdataDir = path.join(dataDir, 'extdata');
const fixtures = path.join(repo, 'server', 'tests');
if (!existsSync(path.join(extdataDir, 'zfin.db'))) {
  mkdirSync(extdataDir, { recursive: true });
  build(
    'zfin_db.py',
    path.join(extdataDir, 'zfin.db'),
    path.join(fixtures, 'zfin_fixture'),
    '--zfin-date',
    'fixture',
  );
  build(
    'labels_db.py',
    path.join(extdataDir, 'labels.db'),
    path.join(fixtures, 'labels_fixture', 'labels.tsv'),
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
