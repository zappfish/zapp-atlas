/** Format checks from the schema's types and patterns. Blank passes; whether a
 *  field is required is decided separately. */

import type { Submission } from "./submission";
import { get, type FieldPath } from "react-hook-form";
import { stageAt } from "./stages";

interface Check {
  validate: (value: unknown, values: Submission) => true | string;
}

const isBlank = (value: unknown) =>
  typeof value !== "string" || value.trim() === "";

const matches = (pattern: RegExp, message: string): Check => ({
  validate: (value) =>
    isBlank(value) || pattern.test((value as string).trim()) || message,
});

const DECIMAL = /^\d+(\.\d+)?$/;

/** QuantityValue.numeric_value. */
export const NUMBER = matches(DECIMAL, "Enter a number, e.g. 10 or 2.5.");

/** Regimen.number_of_individual_exposure: integer. */
export const WHOLE_NUMBER = matches(/^[1-9]\d*$/, "Enter a whole number, e.g. 3.");

export const PERCENT: Check = {
  validate: (value) => {
    if (isBlank(value)) return true;
    const text = (value as string).trim();
    return (DECIMAL.test(text) && Number(text) <= 100) ||
      "Enter a percentage from 0 to 100.";
  },
};

/** Sources that are Study.publication, and so take an identifier. */
export const PUBLISHED_SOURCES = ["PMID", "DOI"];

const PMID_FORMAT = /^(PMID:)?\d+$/i;
const DOI_FORMAT = /^(doi:\s*|https?:\/\/(dx\.)?doi\.org\/)?10\.\d{4,9}\/\S+$/i;

export const PUBLICATION: Check = {
  validate: (value, values) => {
    if (isBlank(value)) return true;
    const text = (value as string).trim();
    switch (values.provenance.sourceType) {
      case "PMID":
        return PMID_FORMAT.test(text) || "Enter a PubMed ID, e.g. 41812223.";
      case "DOI":
        return DOI_FORMAT.test(text) || "Enter a DOI, e.g. 10.1000/xyz123.";
      default:
        return true;
    }
  },
};

/** The annotator slot's pattern, without the ORCID: prefix the form omits. */
export const ORCID = matches(
  /^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/,
  "Enter an ORCID as 0000-0000-0000-0000.",
);

/** The lab slot's pattern; the ZFIN: prefix is optional when typed. */
export const ZFIN_LAB = matches(
  /^(ZFIN:)?ZDB-LAB-\d+-\d+$/,
  "Enter a ZFIN lab ID, e.g. ZDB-LAB-251210-2.",
);

/** Stage slots hold a ZFS term, derived from the number and its unit. */
export const stageTime = (unitName: FieldPath<Submission>): Check => ({
  validate: (value, values) => {
    if (isBlank(value)) return true;
    const text = (value as string).trim();
    if (!DECIMAL.test(text)) return "Enter a number, e.g. 72.";
    const unit = get(values, unitName) as string;
    return stageAt(text, unit) !== undefined || "No ZFS stage covers that time.";
  },
});
