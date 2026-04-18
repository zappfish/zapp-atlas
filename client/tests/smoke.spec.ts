import { expect, test } from '@playwright/test';

test('app loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/ZAPP Atlas/);
});

test('api health ok', async ({ request }) => {
  const apiPort = process.env.API_PORT || '8000';
  const res = await request.get(`http://localhost:${apiPort}/health`);
  expect(res.status()).toBe(200);
  expect(await res.json()).toEqual({ status: 'ok' });
});

test('header renders on home', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('link', { name: 'ZAPP Atlas' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Studies' })).toBeVisible();
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Studies');
});

test('unknown route renders not found', async ({ page }) => {
  await page.goto('/this-route-does-not-exist');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Not found');
  await expect(page.getByRole('link', { name: /back to studies/i })).toBeVisible();
});
