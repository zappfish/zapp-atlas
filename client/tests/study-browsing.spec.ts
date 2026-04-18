import { expect, test } from '@playwright/test';

test('study list shows seeded studies', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Studies');
  await expect(page.getByRole('link', { name: 'PMID:22194820' })).toBeVisible();
  await expect(page.getByRole('link', { name: /DOI:10\.1234\/seed\.example\.002/ })).toBeVisible();
});

test('click-through to study detail renders full graph', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('link', { name: 'PMID:22194820' }).click();
  await expect(page).toHaveURL(/\/studies\/\d+$/);

  // Study header
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('PMID:22194820');

  // Experiment → fish
  await expect(page.getByText('AB', { exact: false }).first()).toBeVisible();
  await expect(page.getByText('ZFIN:ZDB-GENO-960809-7')).toBeVisible();

  // Stressor → chemical name + chebi
  await expect(page.getByText('bisphenol A')).toBeVisible();
  await expect(page.getByText('CHEBI:33216')).toBeVisible();

  // Phenotype observation
  await expect(page.getByText('pericardial region edematous, abnormal')).toBeVisible();

  // Back-link works
  await page.getByRole('link', { name: /all studies/i }).click();
  await expect(page).toHaveURL(/\/$|\/\?/);
});
