import { describe, expect, test } from "vitest";

import { sameBody, toBody, validateBody } from "@/schema/bodies";

/** An experiment as the API returns it, without the level beneath it. */
const SAVED = {
  id: 12,
  standard_rearing_condition: true,
  rearing_condition_comment: null,
  fish: {
    id: 31,
    fish_zfin_id: "ZFIN:ZDB-FISH-160602-1",
    genotype_zfin_id: "ZFIN:ZDB-GENO-160602-1",
    background_zfin_id: "ZFIN:ZDB-GENO-960809-7",
    background_name: "AB",
    allele: [{ id: 44, allele_symbol: "fh111", zygosity: "heterozygous" }],
    transient_reagent: [],
    line_description: null,
  },
  control: [{ id: 7, control_type: "Vehicle control", control_image: [] }],
};

describe("toBody", () => {
  test("leaves out what the server sets, at every depth", () => {
    expect(toBody("Experiment", SAVED)).toEqual({
      standard_rearing_condition: true,
      fish: {
        background_zfin_id: "ZFIN:ZDB-GENO-960809-7",
        background_name: "AB",
        allele: [{ allele_symbol: "fh111", zygosity: "heterozygous" }],
      },
      control: [{ control_type: "Vehicle control" }],
    });
  });

  test("makes a body the schema accepts from a record as it was read", () => {
    const validate = validateBody("Experiment");
    expect(validate(toBody("Experiment", SAVED)), JSON.stringify(validate.errors)).toBe(true);
  });

  test("says nothing of a field left blank", () => {
    const form = { rearing_condition_comment: "   ", standard_rearing_condition: false };
    expect(toBody("Experiment", form)).toEqual({ standard_rearing_condition: false });
  });

  test("leaves out a part with nothing filled in", () => {
    const form = { stressor: [{ chemical_id: "CHEBI:16236", concentration: { unit: "" } }] };
    expect(toBody("ExposureEvent", form)).toEqual({
      stressor: [{ chemical_id: "CHEBI:16236" }],
    });
  });

  test("leaves out a row with nothing filled in", () => {
    const form = { control: [{ control_type: "", comment: " " }, { control_type: "Vehicle control" }] };
    expect(toBody("Experiment", form)).toEqual({
      control: [{ control_type: "Vehicle control" }],
    });
  });

  test("refuses a field the class does not have", () => {
    expect(() => toBody("Experiment", { colour: "red" })).toThrow("no slot named colour");
  });
});

describe("sameBody", () => {
  test("is true of a record and a form that say the same thing", () => {
    const form = {
      control: [{ control_type: "Vehicle control", comment: "" }],
      fish: SAVED.fish,
      standard_rearing_condition: true,
    };
    expect(sameBody("Experiment", SAVED, form)).toBe(true);
  });

  test("is false once the form says something else", () => {
    expect(sameBody("Experiment", SAVED, { ...SAVED, standard_rearing_condition: false })).toBe(false);
  });
});
