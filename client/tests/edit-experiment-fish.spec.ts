import { expect, test } from '@playwright/test';

// Serves two fish to the autocomplete proxy — AB for the initial create, TU
// for the swap on the Edit page.
test.beforeEach(async ({ page }) => {
  let hitCount = 0;
  await page.route('**/api/zfin/fish-autocomplete**', async (route) => {
    hitCount += 1;
    const body =
      hitCount === 1
        ? [
            {
              id: 'ZDB-FISH-150901-28000',
              name: 'AB',
              value: 'AB',
              url: '/ZDB-FISH-150901-28000',
              category: 'Fish',
            },
          ]
        : [
            {
              id: 'ZDB-FISH-150901-29999',
              name: 'TU',
              value: 'TU',
              url: '/ZDB-FISH-150901-29999',
              category: 'Fish',
            },
          ];
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(body),
    });
  });
});

test('swap fish on an edit-experiment page and save', async ({ page }) => {
  // Create a fresh study + experiment so other smoke tests aren't affected
  // by the persisted edit.
  const publication = `PMID:edit-fish-${Date.now()}`;

  await page.goto('/');
  await page.getByRole('link', { name: 'New study' }).click();
  await page.getByLabel('Publication').fill(publication);
  await page.getByLabel('Lab').fill('ZFIN:ZDB-LAB-9999-1');
  await page.getByLabel('Annotators').fill('ORCID:0000-0000-0000-0000');
  await page.getByRole('button', { name: 'Create study' }).click();

  await page.getByRole('link', { name: 'Add experiment' }).click();
  await page.getByRole('radio', { name: /Specific strain/ }).check();
  await page.getByLabel('Fish autocomplete').fill('AB');
  await page.getByRole('button', { name: /AB\b/ }).click();
  await page.getByRole('button', { name: 'Create experiment' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(publication);

  // Edit the experiment and swap the fish.
  await page.getByRole('link', { name: 'Edit', exact: true }).first().click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Edit experiment');

  // Re-enter specific-strain mode (edit starts in wild-type mode by default
  // unless the loaded fish is a known wild-type).
  await page.getByRole('radio', { name: /Specific strain/ }).check();
  await page.getByRole('button', { name: 'change' }).click();
  await page.getByLabel('Fish autocomplete').fill('TU');
  await page.getByRole('button', { name: /TU\b/ }).click();

  // The picked fish is reflected: change button is gone, the new zfin_id
  // appears in the selected row.
  await expect(page.getByText('ZFIN:ZDB-FISH-150901-29999')).toBeVisible();

  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page).toHaveURL(/\/studies\/\d+$/);
  await expect(page.getByText('ZFIN:ZDB-FISH-150901-29999')).toBeVisible();
});
