import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  // Stub OLS so the exposure form can render even without a network.
  await page.route('**/api/ols/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });
});

test('exposure form supports adding and removing stressors', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('link', { name: 'PMID:22194820' }).click();
  await page.getByRole('link', { name: 'Add exposure' }).first().click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New exposure');

  const stressorLegends = page.locator('fieldset.sub-form legend');
  await expect(stressorLegends).toHaveCount(1);
  await expect(stressorLegends.first()).toContainText('Stressor 1');

  await page.getByRole('button', { name: '+ Add stressor' }).click();
  await expect(stressorLegends).toHaveCount(2);
  await expect(stressorLegends.nth(1)).toContainText('Stressor 2');

  await page.getByRole('button', { name: 'Remove stressor 2' }).click();
  await expect(stressorLegends).toHaveCount(1);
});

test('observation form supports adding and removing phenotypes', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('link', { name: 'PMID:22194820' }).click();
  await page.getByRole('link', { name: 'Add observation' }).first().click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New observation');

  const phenoLegends = page.locator('fieldset.sub-form legend');
  await expect(phenoLegends).toHaveCount(1);
  await expect(phenoLegends.first()).toContainText('Phenotype 1');

  await page.getByRole('button', { name: '+ Add phenotype' }).click();
  await expect(phenoLegends).toHaveCount(2);
  await expect(phenoLegends.nth(1)).toContainText('Phenotype 2');

  await page.getByRole('button', { name: 'Remove phenotype 1' }).click();
  await expect(phenoLegends).toHaveCount(1);
});
