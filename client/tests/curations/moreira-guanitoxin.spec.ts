/**
 * Curate Moreira et al. 2025 — "Environmental Mixture Toxicity of Guanitoxin
 * and Organophosphates in Zebrafish" (Env. Sci. Technol., PMID:41812223,
 * DOI:10.1021/acs.est.5c16673, CC-BY 4.0). Figure 2 shows pericardial
 * edema at 120 hpf on trichlorfon + guanitoxin co-exposed embryos.
 *
 * This spec exercises the full form path end-to-end against real
 * zapp-atlas services, stubbing only the external ZFIN / OLS endpoints.
 * On success the curated study is persisted into the dev DB and can be
 * promoted to ``server/seed.py`` via ``just export-seed``.
 */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

import { expect, test } from '@playwright/test';

import {
  createStudyViaForm,
  fillStressor,
  pickWildType,
  stubOlsAutocomplete,
  stubOlsValidation,
} from './_helpers';

const PUBLICATION = 'PMID:41812223';
const FIGURE_PATH = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../..',
  'docs/curation-fixtures/moreira-guanitoxin-fig2.jpg',
);

test('curate Moreira et al. 2025 guanitoxin + OP mixture study', async ({ page }) => {
  // ---- stubs ----------------------------------------------------------
  await stubOlsAutocomplete(page, {
    route: [
      { term_uri: 'ExO:0000161', term_label: 'ambient acquatic environment route' },
    ],
    exposureType: [
      { term_uri: 'ECTO:9001150', term_label: 'exposure to malathion' },
    ],
  });
  await stubOlsValidation(page, [
    {
      curie: 'ExO:0000161',
      ontology: 'exo',
      label: 'ambient acquatic environment route',
      ancestors: ['ExO:0000055'],
    },
    {
      curie: 'ECTO:9001150',
      ontology: 'ecto',
      label: 'exposure to malathion',
    },
  ]);

  // ---- study ---------------------------------------------------------
  const studyId = await createStudyViaForm(page, {
    publication: PUBLICATION,
    lab: 'ZFIN:ZDB-LAB-0004-01',
    annotators: 'ORCID:0000-0004-0404-0404',
  });

  // ---- experiment ----------------------------------------------------
  await page.getByRole('link', { name: 'Add experiment' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New experiment');
  await pickWildType(page, 'AB');
  await page.getByRole('button', { name: 'Create experiment' }).click();
  await expect(page).toHaveURL(new RegExp(`/studies/${studyId}$`));

  // ---- exposure ------------------------------------------------------
  await page.getByRole('link', { name: 'Add exposure' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New exposure');

  // NB: EXO has a typo — the term is spelled "acquatic", not "aquatic".
  // Search by "ambient" to avoid hinting at that upstream quirk.
  await page.getByLabel('Route autocomplete').fill('ambient');
  await page.getByRole('button', { name: /ambient acquatic/ }).click();

  await page.getByLabel('Exposure type autocomplete').fill('malathion');
  await page.getByRole('button', { name: /exposure to malathion/ }).click();

  await page.getByLabel('Start stage').fill('ZFS:0000016');
  await page.getByLabel('End stage').fill('ZFS:0000050');

  await fillStressor(page, 0, {
    chemical_name: 'malathion',
    chebi_id: 'CHEBI:6651',
    cas_id: '121-75-5',
    concentration: '5',
    unit: 'µM',
  });
  await page.getByRole('button', { name: '+ Add stressor' }).click();
  await fillStressor(page, 1, {
    chemical_name: 'trichlorfon',
    chebi_id: 'CHEBI:9747',
    cas_id: '52-68-6',
    concentration: '1',
    unit: 'µM',
  });

  await page.getByLabel('Comment').fill(
    'Trichlorfon + guanitoxin co-exposure potentiated pericardial edema beyond either alone (Moreira et al. 2025 Fig. 2).',
  );

  await page.getByRole('button', { name: 'Create exposure' }).click();
  await expect(page).toHaveURL(new RegExp(`/studies/${studyId}$`));

  // ---- observation ---------------------------------------------------
  await page.getByRole('link', { name: 'Add observation' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New observation');

  await page.getByLabel('Observation stage 1').fill('ZFS:0000050');
  await page.getByLabel('Severity').selectOption('severe');
  await page.getByLabel('Prevalence').fill('100');

  // CURIE input (not the picker) for deterministic runs.
  const curieInput = page.getByLabel('Phenotype CURIE 1');
  await curieInput.fill('ZP:0105827');
  await curieInput.press('Enter');
  await expect(page.getByText('ZP:0105827', { exact: true })).toBeVisible();

  // Attach Figure 2 if present on disk (the spec works without it; the
  // image upload is exercised in exposure-observation.spec.ts separately).
  try {
    const buffer = readFileSync(FIGURE_PATH);
    await page.getByLabel('Image files').setInputFiles({
      name: 'moreira-fig2.jpg',
      mimeType: 'image/jpeg',
      buffer,
    });
  } catch {
    /* fixture not present — continue without image */
  }

  await page.getByRole('button', { name: 'Create observation' }).click();
  await expect(page).toHaveURL(new RegExp(`/studies/${studyId}$`));

  // ---- round-trip assertions on the detail page ---------------------
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(PUBLICATION);
  await expect(page.getByText('malathion', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('trichlorfon', { exact: true })).toBeVisible();
  await expect(page.getByText('ZP:0105827').first()).toBeVisible();
  await expect(page.getByText('ambient acquatic environment route').first()).toBeVisible();
  await expect(page.getByText('exposure to malathion').first()).toBeVisible();
});
