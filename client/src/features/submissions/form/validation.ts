/** Checks the observation form still makes by hand. They give way to the
 *  schema's when that form is pointed at the schema's fields. */

import type { Submission } from "./submission";

interface Check {
  validate: (value: unknown, values: Submission) => true | string;
}

const isBlank = (value: unknown) =>
  typeof value !== "string" || value.trim() === "";

const DECIMAL = /^\d+(\.\d+)?$/;

export const PERCENT: Check = {
  validate: (value) => {
    if (isBlank(value)) return true;
    const text = (value as string).trim();
    return (DECIMAL.test(text) && Number(text) <= 100) ||
      "Enter a percentage from 0 to 100.";
  },
};
