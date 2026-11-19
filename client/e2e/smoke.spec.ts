/**
 * A smoke test of the whole stack: the server-rendered pages, development
 * sign-in, the React client, and the API behind it.
 *
 * It checks that the pieces are connected, not how each screen behaves.
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

test("a group's page lists its fish tank, chemical cabinet and studies", async ({
  page,
}) => {
  await signIn(page);
  await page.getByRole("link", { name: GROUP }).click();

  await expect(page.getByRole("heading", { name: GROUP })).toBeVisible();
  await expect(page.getByText("ZFIN:ZDB-GENO-960809-7")).toBeVisible();
  await expect(page.getByText("CHEBI:33216")).toBeVisible();
  // One of the studies the seed gives the group.
  await expect(page.getByText("PMID:22194820")).toBeVisible();
});

test("a study added on the group page is saved as a draft, and listed", async ({
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

  // Back on the group's page, the new study is in its list.
  await page.goto(page.url().replace(/\/studies\/\d+$/, ""));
  const studies = page.locator("#studies");
  const more = studies.getByRole("button", { name: /View \d+ more/ });
  if (await more.isVisible()) await more.click();
  await expect(studies.getByText("Smoke test study")).toBeVisible();
});

test("a study's own fields are edited on its page, and checked as the schema says", async ({
  page,
}) => {
  await signIn(page);
  const groups = await (await page.request.get("/api/research-groups")).json();
  const study = await (
    await page.request.post("/api/studies", {
      data: { research_group: groups[0].id, status: "draft", nickname: "Edit me" },
    })
  ).json();
  await page.goto(`/research-groups/${groups[0].id}/studies/${study.id}`);

  await page.getByLabel("Actions for Edit me").click();
  await page.getByRole("menuitem", { name: "Edit" }).click();
  const dialog = page.getByRole("dialog");
  // The nickname it was saved with is there to change.
  await expect(dialog.getByPlaceholder("e.g. Tamoxifen heart study")).toHaveValue("Edit me");

  // The schema says what a publication looks like, and gives the example.
  const publication = dialog.getByPlaceholder("PMID:41812223 or DOI:10.1000/xyz123");
  await publication.fill("in press");
  await dialog.getByRole("button", { name: "Save" }).click();
  await expect(dialog.getByText("Enter this in the form PMID:22194820.")).toBeVisible();

  await publication.fill("PMID:41812223");
  await dialog.getByPlaceholder("What the study sets out to do").fill("Edited on its page");
  await dialog.getByRole("button", { name: "Save" }).click();
  await expect(dialog).toBeHidden();
  await expect(page.getByText("Edited on its page")).toBeVisible();

  const stored = await (await page.request.get(`/api/studies/${study.id}`)).json();
  expect(stored).toMatchObject({
    publication: "PMID:41812223",
    nickname: "Edit me",
    description: "Edited on its page",
    // Left as it was: a body carries the group and status it was read with.
    status: "draft",
    research_group: groups[0].id,
  });
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

test("a fish described in the tank dialog gets its ZFIN ids, and the form offers it", async ({
  page,
}) => {
  await signIn(page);
  await page.getByRole("link", { name: GROUP }).click();
  await page.getByRole("button", { name: "+ Add fish" }).click();

  // The lines and alleles come from server/tests/zfin_fixture: fh111 is
  // registered heterozygous on AB as ZDB-GENO-160602-1 / ZDB-FISH-160602-1.
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Wild-type background").selectOption({ label: "AB" });
  await dialog.getByPlaceholder(/Allele \(fh111\)/).fill("fh111");
  await dialog.getByRole("button", { name: /^fh111/ }).click();
  await expect(dialog.getByText(/1 allele still needs a zygosity/)).toBeVisible();
  await dialog.getByLabel("Zygosity in this fish").selectOption("heterozygous");
  await expect(dialog.getByText("Matches ZFIN fish ZFIN:ZDB-FISH-160602-1", { exact: false })).toBeVisible();
  await dialog.getByPlaceholder("What this group calls the line").fill("fh111 carriers");
  await dialog.getByRole("button", { name: "Add to tank" }).click();

  // Listed under its nickname, with the genotype ZFIN matched.
  const tank = page.locator("#fish-tank");
  await expect(tank.getByText("fh111 carriers")).toBeVisible();
  await expect(tank.getByText("ZFIN:ZDB-GENO-160602-1")).toBeVisible();

  // Stored as described, with the ids the server matched.
  const groups = await (await page.request.get("/api/research-groups")).json();
  const entries = await (
    await page.request.get(`/api/research-groups/${groups[0].id}/fish-tank`)
  ).json();
  const saved = entries.find((e: { nickname: string | null }) => e.nickname === "fh111 carriers");
  expect(saved.fish).toMatchObject({
    background_zfin_id: "ZFIN:ZDB-GENO-960809-7",
    background_name: "AB",
    genotype_zfin_id: "ZFIN:ZDB-GENO-160602-1",
    fish_zfin_id: "ZFIN:ZDB-FISH-160602-1",
    allele: [
      {
        allele_zfin_id: "ZFIN:ZDB-ALT-160602-14",
        allele_symbol: "fh111",
        alteration_type: "point_mutation",
        affected_gene_symbol: "snapc1b",
        zygosity: "heterozygous",
        // Left alone in the dialog, so not recorded.
        mother_zygosity: null,
        father_zygosity: null,
      },
    ],
  });

  // A new experiment's form offers the tank's lines, and shows the chosen one.
  const study = await (
    await page.request.post("/api/studies", {
      data: { research_group: groups[0].id, status: "draft", nickname: "Tank test" },
    })
  ).json();
  await page.goto(
    `/research-groups/${groups[0].id}/studies/${study.id}/experiments/new`,
  );
  await page
    .getByLabel("Select a fish line from your tank")
    .selectOption({ label: "fh111 carriers — fh111/+ (AB)" });
  const fish = page.locator("#fish");
  await expect(fish.getByText("fh111 carriers")).toBeVisible();
  await expect(fish.getByText(/ZFIN:ZDB-GENO-160602-1/)).toBeVisible();
});

test("an experiment is set up on its page, saved, reopened and changed", async ({
  page,
}) => {
  await signIn(page);
  const groups = await (await page.request.get("/api/research-groups")).json();
  const study = await (
    await page.request.post("/api/studies", {
      data: { research_group: groups[0].id, status: "draft", nickname: "Experiment test" },
    })
  ).json();
  const stored = async () =>
    (await (await page.request.get(`/api/studies/${study.id}`)).json()).experiment;

  await page.goto(`/research-groups/${groups[0].id}/studies/${study.id}`);
  await page.getByRole("link", { name: "+ New experiment" }).click();
  await expect(page.getByRole("heading", { name: "New experiment" })).toBeVisible();
  // Nothing hangs off an experiment that has not been saved.
  await expect(page.getByText("Save the experiment to add its exposure events.")).toBeVisible();

  // The setup: a fish from the tank, how it was kept, and a control.
  await page.getByLabel("Select a fish line from your tank").selectOption({ index: 1 });
  await page.getByRole("radio", { name: "Non-standard" }).check();
  await page.getByRole("textbox", { name: "Describe the conditions" }).fill("Kept in the dark");
  await page.getByRole("radio", { name: "Vehicle control" }).check();
  await page.getByLabel("Vehicle used").selectOption("dmso");
  await page.getByRole("textbox", { name: "Vehicle concentration" }).fill("0.1");
  await page.getByRole("button", { name: "Save experiment" }).click();

  // Saved, and now at the address named for it.
  await expect(page).toHaveURL(/\/experiments\/\d+$/);
  await expect(page.getByRole("heading", { name: "Experiment", exact: true })).toBeVisible();

  // An exposure event is saved on its own, and checked before it is sent.
  await page.getByRole("button", { name: "+ Add an exposure event" }).click();
  const group = page.getByRole("form", { name: "Exposure event 1" });
  await group.getByLabel("Select a chemical from your cabinet").selectOption({ index: 1 });
  await group.getByRole("textbox", { name: "Substance concentration" }).fill("10");
  // A vehicle's concentration is refused without the vehicle it is of.
  await group.getByRole("textbox", { name: "Vehicle concentration" }).fill("0.1");
  await group.getByRole("textbox", { name: "Start stage" }).fill("6");
  await group.getByRole("textbox", { name: "End stage" }).fill("2");
  await group.getByRole("button", { name: "Save exposure event" }).click();
  await expect(group.getByText("Must not be before the start stage.")).toBeVisible();
  await expect(group.getByText("This is required.")).toBeVisible();
  await group.getByLabel("Vehicle of dilution").selectOption("dmso");
  await group.getByRole("textbox", { name: "End stage" }).fill("120");
  await group.getByLabel("Additional exposure condition").fill("Plates sealed");
  await group.getByRole("button", { name: "Save exposure event" }).click();
  // Folded to a line once saved.
  await expect(group.getByRole("button", { name: "Save exposure event" })).toBeHidden();
  await expect(group.getByText(/10 µM/)).toBeVisible();

  expect(await stored()).toMatchObject([
    {
      standard_rearing_condition: false,
      rearing_condition_comment: "Kept in the dark",
      fish: { background_name: "AB" },
      control: [
        {
          control_type: "Vehicle control",
          vehicle_if_treated: {
            vehicle_type: "dmso",
            concentration: { numeric_value: 0.1, unit: "%" },
          },
        },
      ],
      exposure_event: [
        {
          route: "aquatic_environment",
          regimen: { exposure_regimen_type: "continuous" },
          stressor: [{ concentration: { numeric_value: 10, unit: "µM" } }],
          vehicle: [{ vehicle_type: "dmso", concentration: { numeric_value: 0.1, unit: "%" } }],
          // 6 hpf and 120 hpf, as the stages they fall in.
          exposure_start_stage: "ZFS:0000019",
          exposure_end_stage: "ZFS:0000037",
          additional_exposure_condition: "Plates sealed",
        },
      ],
    },
  ]);

  // Opened again, it holds what was saved, and a change to it is a replacement.
  await page.reload();
  const conditions = page.getByRole("textbox", { name: "Describe the conditions" });
  await expect(conditions).toHaveValue("Kept in the dark");
  await conditions.fill("Kept at 30 degrees");
  await page.getByRole("button", { name: "Save experiment" }).click();
  await expect(page.getByText("Changes not saved.")).toBeHidden();

  const [experiment] = await stored();
  expect(experiment.rearing_condition_comment).toBe("Kept at 30 degrees");
  // What the form did not change is as it was, the fish and control included.
  expect(experiment.fish).toMatchObject({ background_name: "AB" });
  expect(experiment.control).toHaveLength(1);
  // Saving the experiment leaves its exposure events alone.
  expect(experiment.exposure_event).toHaveLength(1);

  // The study's page lists it.
  await page.goto(`/research-groups/${groups[0].id}/studies/${study.id}`);
  await expect(page.locator("#experiments").getByText("1 exposure event")).toBeVisible();
});
