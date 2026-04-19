import { expect, test } from '@playwright/test';

const ZFIN_AUTOCOMPLETE_PATH = '**/api/zfin/fish-autocomplete**';

test.beforeEach(async ({ page }) => {
  // Stub the ZFIN proxy so smoke runs are deterministic and offline-safe.
  await page.route(ZFIN_AUTOCOMPLETE_PATH, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'ZDB-FISH-150901-27842',
          name: 'AB',
          value: 'AB',
          url: '/ZDB-FISH-150901-27842',
          category: 'Fish',
        },
        {
          id: 'ZDB-FISH-150901-27843',
          name: 'TU',
          value: 'TU',
          url: '/ZDB-FISH-150901-27843',
          category: 'Fish',
        },
      ]),
    });
  });
});

test('create study, add experiment via ZFIN autocomplete, then edit the study', async ({
  page,
}) => {
  // Unique publication so repeated runs don't collide with earlier runs.
  const publication = `PMID:smoke-${Date.now()}`;
  const editedPublication = `PMID:smoke-edited-${Date.now()}`;

  // Home → New study
  await page.goto('/');
  await page.getByRole('link', { name: 'New study' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New study');

  // Fill and submit study form
  await page.getByLabel('Publication').fill(publication);
  await page.getByLabel('Lab').fill('ZFIN:ZDB-LAB-9999-1');
  await page.getByLabel('Annotators').fill('ORCID:0000-0000-0000-0000');
  await page.getByRole('button', { name: 'Create study' }).click();

  await expect(page).toHaveURL(/\/studies\/\d+$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(publication);

  // Add experiment via ZFIN autocomplete
  await page.getByRole('link', { name: 'Add experiment' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New experiment');

  await page.getByLabel('Fish autocomplete').fill('AB');
  await page.getByRole('button', { name: /AB\b/ }).click();
  await expect(page.getByText('ZFIN:ZDB-FISH-150901-27842')).toBeVisible();

  await page.getByRole('button', { name: 'Create experiment' }).click();
  await expect(page).toHaveURL(/\/studies\/\d+$/);
  await expect(page.getByRole('heading', { level: 2, name: 'Experiments' })).toBeVisible();
  await expect(page.getByText('ZFIN:ZDB-FISH-150901-27842')).toBeVisible();

  // Edit the study's publication
  await page.getByRole('link', { name: 'Edit study' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Edit study');
  await page.getByLabel('Publication').fill(editedPublication);
  await page.getByRole('button', { name: 'Save' }).click();

  await expect(page).toHaveURL(/\/studies\/\d+$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(editedPublication);
});
