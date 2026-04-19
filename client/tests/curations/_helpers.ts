/**
 * Shared Playwright helpers for paper-curation specs.
 *
 * Each spec in ./curations drives the real form UI to enter a published
 * study. These helpers stub external HTTP that would otherwise make the
 * run slow or flaky: ZFIN quicksearch, OLS autocomplete + validation.
 * Local assets (ZFA/ZP ontology JSON used by the phenotype picker, the
 * wild-type list from our own API) are untouched.
 */

import { expect, type Page } from '@playwright/test';

export interface ZfinHit {
  id: string;
  name: string;
}

/**
 * Stub the ZFIN quicksearch proxy so a specific-strain search returns the
 * provided hits regardless of query. Matches on any ``q`` substring.
 */
export async function stubZfinAutocomplete(page: Page, hits: ZfinHit[]): Promise<void> {
  await page.route('**/api/zfin/fish-autocomplete**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(
        hits.map((h) => ({
          id: h.id,
          name: h.name,
          value: h.name,
          url: `/${h.id}`,
          category: 'Fish',
        })),
      ),
    });
  });
}

export interface OlsHit {
  term_uri: string;
  term_label: string;
}

/**
 * Stub the OLS autocomplete proxy for route and/or exposure type. Any
 * entry whose label contains the current query substring (case-insensitive)
 * is returned.
 */
export async function stubOlsAutocomplete(
  page: Page,
  opts: { route?: OlsHit[]; exposureType?: OlsHit[] },
): Promise<void> {
  const filter = (hits: OlsHit[], q: string): OlsHit[] => {
    const ql = q.toLowerCase();
    return hits.filter(
      (h) => h.term_label.toLowerCase().includes(ql) || h.term_uri.toLowerCase().includes(ql),
    );
  };

  if (opts.route) {
    const hits = opts.route;
    await page.route('**/api/ols/exposure-route-autocomplete**', async (route) => {
      const q = new URL(route.request().url()).searchParams.get('q') ?? '';
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(filter(hits, q)),
      });
    });
  }
  if (opts.exposureType) {
    const hits = opts.exposureType;
    await page.route('**/api/ols/exposure-type-autocomplete**', async (route) => {
      const q = new URL(route.request().url()).searchParams.get('q') ?? '';
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(filter(hits, q)),
      });
    });
  }
}

export interface OlsTerm {
  curie: string;
  ontology: string;
  label: string;
  /** CURIEs of ancestors OLS will report. Include root nodes used by
   * reachability checks (ExO:0000055 for route, none for exposure_type). */
  ancestors?: string[];
}

/**
 * Stub the upstream OLS4 calls that ``server/ontology.py`` makes at
 * insert-time: the term lookup and the ancestors lookup. One stub per
 * ``(curie, ontology)`` pair is required because the server caches by
 * that key between requests.
 */
export async function stubOlsValidation(page: Page, terms: OlsTerm[]): Promise<void> {
  await page.route('**/ols4/api/**', async (route) => {
    const url = route.request().url();
    const isAncestors = url.includes('/ancestors');
    const ontologyMatch = url.match(/\/ontologies\/([a-z0-9]+)\//);
    const ontology = ontologyMatch ? ontologyMatch[1] : '';

    // Find the term whose OBO short-form appears in the URL; fall back to
    // the IRI query param when that's the parameter used (term lookup).
    const asShort = (curie: string) => curie.replace(':', '_');
    const iri = new URL(url).searchParams.get('iri') ?? '';
    const term = terms.find(
      (t) =>
        t.ontology === ontology &&
        (url.includes(asShort(t.curie)) || iri.includes(asShort(t.curie))),
    );

    if (!term) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ _embedded: { terms: [] } }),
      });
      return;
    }

    if (isAncestors) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          _embedded: {
            terms: (term.ancestors ?? []).map((a) => ({ obo_id: a, label: a })),
          },
        }),
      });
      return;
    }

    // Term lookup.
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        _embedded: {
          terms: [
            {
              iri: `http://purl.obolibrary.org/obo/${asShort(term.curie)}`,
              obo_id: term.curie,
              label: term.label,
            },
          ],
        },
      }),
    });
  });
}

export interface StudyForm {
  publication: string;
  lab: string;
  annotators: string;
}

/** Click "New study", fill the form, submit. Returns the new study id. */
export async function createStudyViaForm(page: Page, form: StudyForm): Promise<string> {
  await page.goto('/');
  await page.getByRole('link', { name: 'New study' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('New study');

  await page.getByLabel('Publication').fill(form.publication);
  await page.getByLabel('Lab').fill(form.lab);
  await page.getByLabel('Annotators').fill(form.annotators);
  await page.getByRole('button', { name: 'Create study' }).click();

  await expect(page).toHaveURL(/\/studies\/\d+$/);
  const url = page.url();
  const match = url.match(/\/studies\/(\d+)$/);
  if (!match) throw new Error(`unexpected URL after create: ${url}`);
  return match[1]!;
}

/**
 * On a form with a FishPicker, pick a curated wild-type by its display
 * name (``AB``, ``Tübingen``, …). Matches the start of the option label.
 */
export async function pickWildType(page: Page, name: string): Promise<void> {
  await page.getByRole('radio', { name: /Wild-type background/ }).check();
  const select = page.getByLabel('Wild-type genotype');
  const value = await select.locator('option').evaluateAll(
    (options, wanted) => {
      for (const o of options as HTMLOptionElement[]) {
        if ((o.textContent ?? '').trim().startsWith(`${wanted} `)) {
          return o.value;
        }
      }
      return null;
    },
    name,
  );
  if (!value) throw new Error(`Wild-type "${name}" not found in dropdown`);
  await select.selectOption(value);
}

export interface StressorForm {
  chemical_name: string;
  chebi_id: string;
  cas_id: string;
  uri?: string;
  concentration?: string;
  unit?: string;
  manufacturer?: string;
}

/**
 * Fill the N-th stressor fieldset on an exposure form. Index is 0-based
 * — use ``+ Add stressor`` ahead of this for additional rows.
 */
export async function fillStressor(
  page: Page,
  index: number,
  s: StressorForm,
): Promise<void> {
  const fieldset = page.locator('fieldset.sub-form').nth(index);
  const inputs = fieldset.locator('input');

  await inputs.nth(0).fill(s.chemical_name);
  await inputs.nth(1).fill(s.chebi_id);
  await inputs.nth(2).fill(s.cas_id);
  await inputs.nth(3).fill(s.uri ?? `http://purl.obolibrary.org/obo/${s.chebi_id.replace(':', '_')}`);
  if (s.concentration) await inputs.nth(4).fill(s.concentration);
  if (s.unit) await inputs.nth(5).fill(s.unit);
  if (s.manufacturer) await inputs.nth(6).fill(s.manufacturer);
}
