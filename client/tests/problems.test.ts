import type { ResolverOptions } from "react-hook-form";
import { describe, expect, test } from "vitest";

import { bodyResolver } from "@/problems";

const options = {} as ResolverOptions<Record<string, unknown>>;

describe("bodyResolver", () => {
  test("passes values that make a body the schema accepts", async () => {
    const values = { research_group: 1, status: "draft", nickname: "BPA pilot" };
    const result = await bodyResolver("Study")(values, undefined, options);

    expect(result).toEqual({ values, errors: {} });
  });

  test("puts a missing required field's problem on that field", async () => {
    // With no publication, a study must have a nickname.
    const values = { research_group: 1, status: "draft", nickname: "" };
    const { errors } = await bodyResolver("Study")(values, undefined, options);

    expect(errors.nickname).toMatchObject({ type: "schema", message: "This is required." });
  });

  test("puts a nested problem on the nested field, by the form's own name for it", async () => {
    const values = { stressor: [{ chemical_id: "CHEBI:16236", concentration: { numeric_value: -1 } }] };
    const { errors } = await bodyResolver("ExposureEvent")(values, undefined, options);

    expect(errors).toMatchObject({
      stressor: [{ concentration: { numeric_value: { type: "schema" } } }],
    });
  });

  test("counts rows as the form has them, blank ones included", async () => {
    // The first control is blank, so the body's first is the form's second.
    const values = {
      control: [{}, { vehicle_if_treated: { vehicle_type: "other_not_listed" } }],
    };
    const { errors } = await bodyResolver("Experiment")(values, undefined, options);

    expect(errors).toMatchObject({
      control: [
        undefined,
        { vehicle_if_treated: { unrecognized_chemical_name: { message: "This is required." } } },
      ],
    });
  });

  test("says what a number should be", async () => {
    const values = { phenotype: [{ prevalence: 120 }, { prevalence: "most" }] };
    const { errors } = await bodyResolver("PhenotypeObservationSet")(values, undefined, options);

    expect(errors).toMatchObject({
      phenotype: [
        { prevalence: { message: "Enter 100 or less." } },
        { prevalence: { message: "Enter a number." } },
      ],
    });
  });
});

describe("toProblems", () => {
  test("keeps one problem per field: the one about its value", async () => {
    // An optional enum: Ajv also says "must be null" and "must match anyOf".
    const values = { stressor: [{ chemical_id: "CHEBI:16236", manufacturer: "acme" }] };
    const { errors } = await bodyResolver("ExposureEvent")(values, undefined, options);

    expect(errors).toMatchObject({
      stressor: [{ manufacturer: { message: "must be equal to one of the allowed values" } }],
    });
  });

  test("puts a rule about several fields on each of them", async () => {
    // A stressor needs a chemical id or, failing that, a name.
    const values = { stressor: [{ comment: "from the old stock" }] };
    const { errors } = await bodyResolver("ExposureEvent")(values, undefined, options);

    expect(errors).toMatchObject({
      stressor: [
        {
          chemical_id: { message: "This is required." },
          unrecognized_chemical_name: { message: "This is required." },
        },
      ],
    });
  });

  test("shows what a pattern asks for, from the schema's example", async () => {
    const values = { research_group: 1, status: "draft", publication: "soon", lab: "our lab" };
    const { errors } = await bodyResolver("Study")(values, undefined, options);

    expect(errors).toMatchObject({
      publication: { message: "Enter this in the form PMID:22194820." },
      lab: { message: "Enter this in the form ZFIN:ZDB-LAB-970408-1." },
    });
  });
});
