import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.route('**/api/ols/exposure-route-autocomplete**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { term_uri: 'ExO:0000057', term_label: 'inhalation route' },
      ]),
    });
  });
  await page.route('**/api/ols/exposure-type-autocomplete**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { term_uri: 'ECTO:0000001', term_label: 'exposure to stressor' },
      ]),
    });
  });
  // Short-circuit OLS term + ancestors lookups that the server makes when
  // validating on POST.
  await page.route('**/ols4/api/**', async (route) => {
    const url = route.request().url();
    if (url.includes('/ancestors')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          _embedded: {
            terms: [{ obo_id: 'ExO:0000055', label: 'exposure route' }],
          },
        }),
      });
      return;
    }
    if (url.includes('/ontologies/exo/terms') || url.includes('/ontologies/ecto/terms')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          _embedded: {
            terms: [
              {
                iri: 'http://purl.obolibrary.org/obo/ExO_0000057',
                obo_id: 'ExO:0000057',
                label: 'inhalation route',
              },
            ],
          },
        }),
      });
      return;
    }
    await route.continue();
  });
});

test('add exposure via OLS autocomplete and attach observation with image', async ({
  page,
}) => {
  // Start from the seeded BPA study.
  await page.goto('/');
  await page.getByRole('link', { name: 'PMID:22194820' }).click();

  // First experiment on that study — click Add exposure.
  await page.getByRole('link', { name: 'Add exposure' }).first().click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New exposure');

  // Route autocomplete
  await page.getByLabel('Route autocomplete').fill('inh');
  await page.getByRole('button', { name: /inhalation route/ }).click();
  await expect(page.getByText('ExO:0000057')).toBeVisible();

  // Exposure type autocomplete (same OLS stubbing serves both)
  await page.getByLabel('Exposure type autocomplete').fill('exp');
  await page.getByRole('button', { name: /exposure to stressor/ }).click();

  // Start / end stage
  await page.getByLabel('Start stage').fill('ZFS:0000011');
  await page.getByLabel('End stage').fill('ZFS:0000039');

  await page.getByRole('button', { name: 'Create exposure' }).click();

  // Back on study detail; new exposure should show the picked route label
  // alongside the existing seeded one.
  await expect(page).toHaveURL(/\/studies\/\d+$/);
  await expect(page.getByText('ExO:0000057').first()).toBeVisible();

  // Add an observation to the exposure we just created. Use .last() since
  // the seeded exposure already has an observation.
  await page.getByRole('link', { name: 'Add observation' }).last().click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New observation');

  await page.getByLabel('Observation stage').fill('ZFS:0000035');

  // Upload a 1x1 PNG as an image attachment
  const pngBytes = Buffer.from(
    '89504E470D0A1A0A0000000D49484452000000010000000108020000' +
      '00907753DE0000000C4944415408D76368F8FF1F0000040100017F3F' +
      '8F180000000049454E44AE426082',
    'hex',
  );
  await page.getByLabel('Image files').setInputFiles({
    name: 'smoke.png',
    mimeType: 'image/png',
    buffer: pngBytes,
  });

  await page.getByRole('button', { name: 'Create observation' }).click();

  // Back on study detail, the new observation's image should render.
  await expect(page).toHaveURL(/\/studies\/\d+$/);
  const imgs = page.locator('img[alt*="image"]');
  await expect(imgs.last()).toBeVisible();
});
