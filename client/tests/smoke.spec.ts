import { expect, test } from '@playwright/test';

test('app loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/.+/);
});

test('api health ok', async ({ request }) => {
  const apiPort = process.env.API_PORT || '8000';
  const res = await request.get(`http://localhost:${apiPort}/health`);
  expect(res.status()).toBe(200);
  expect(await res.json()).toEqual({ status: 'ok' });
});
