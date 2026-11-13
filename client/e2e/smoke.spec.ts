/**
 * A smoke test of the whole stack: the server-rendered pages, development
 * sign-in, the React client, and the API behind it.
 *
 * It checks that the pieces are connected, not how each screen behaves. The
 * submission form does not save to the server yet, so beyond adding a study
 * on the group page, the study routes are exercised here through the
 * signed-in browser session.
 *
 * See playwright.config.ts for how the server is started.
 */

import { expect, test, type Page } from "@playwright/test";

/** The group the seed gives the development identity. */
const GROUP = "Zebrafish Toxicology Lab";

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Sign in as Josiah Carberry" }).click();
  await expect(page).toHaveURL(/\/my-submissions$/);
}

test("a signed-out visitor is sent to sign in", async ({ page }) => {
  await page.goto("/my-submissions");
  await expect(page).toHaveURL(/\/login$/);
});

test("signing in shows the caller's research group", async ({ page }) => {
  await signIn(page);
  await expect(page.getByRole("link", { name: GROUP })).toBeVisible();
});

test("a group's page lists its fish tank and chemical cabinet", async ({
  page,
}) => {
  await signIn(page);
  await page.getByRole("link", { name: GROUP }).click();

  await expect(page.getByRole("heading", { name: GROUP })).toBeVisible();
  await expect(page.getByText("ZFIN:ZDB-GENO-960809-7")).toBeVisible();
  await expect(page.getByText("CHEBI:33216")).toBeVisible();
});

test("the submission form opens for a group", async ({ page }) => {
  await signIn(page);
  await page.getByRole("link", { name: GROUP }).click();
  await page.getByRole("link", { name: "+ New Submission" }).click();

  await expect(
    page.getByRole("heading", { name: "Annotate your data" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Save draft" })).toBeVisible();
});

test("a study added on the group page is saved as a draft", async ({
  page,
  playwright,
}) => {
  await signIn(page);
  await page.getByRole("link", { name: GROUP }).click();
  await page.getByRole("button", { name: "+ New study" }).click();

  const dialog = page.getByRole("dialog");
  await dialog.getByRole("combobox").selectOption("unpublished");
  await dialog.getByPlaceholder("e.g. Tamoxifen heart study").fill("Smoke test study");
  await dialog.getByRole("button", { name: "Add study" }).click();

  // Creating a study opens its own page.
  await expect(page).toHaveURL(/\/studies\/\d+$/);
  await expect(page.getByText("Smoke test study").first()).toBeVisible();

  const id = page.url().split("/").pop();
  const stored = await (await page.request.get(`/api/studies/${id}`)).json();
  expect(stored).toMatchObject({ nickname: "Smoke test study", status: "draft" });

  // A draft is not visible to someone who is not signed in.
  const anonymous = await playwright.request.newContext({
    baseURL: new URL(page.url()).origin,
  });
  expect((await anonymous.get(`/api/studies/${id}`)).status()).toBe(404);
  await anonymous.dispose();
});

test("the signed-in session can save a study, and a draft stays private", async ({
  page,
  playwright,
}) => {
  await signIn(page);
  const groups = await (await page.request.get("/api/research-groups")).json();

  const created = await page.request.post("/api/studies", {
    data: {
      research_group: groups[0].id,
      status: "draft",
      nickname: "Smoke test pilot",
    },
  });
  expect(created.status()).toBe(201);
  const study = await created.json();

  const replaced = await page.request.put(`/api/studies/${study.id}`, {
    data: {
      research_group: groups[0].id,
      status: "draft",
      nickname: "Smoke test pilot",
      description: "Edited",
    },
  });
  expect(replaced.status()).toBe(200);
  expect((await replaced.json()).description).toBe("Edited");

  // Someone who is not signed in cannot see a draft, or write to anything.
  const anonymous = await playwright.request.newContext({
    baseURL: new URL(page.url()).origin,
  });
  expect((await anonymous.get(`/api/studies/${study.id}`)).status()).toBe(404);
  expect(
    (await anonymous.post("/api/studies", { data: {} })).status(),
  ).toBe(401);
  await anonymous.dispose();
});
