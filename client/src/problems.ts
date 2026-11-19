/**
 * What is wrong with a request body, in one shape whichever side found it:
 * the client's check against the schema, or the server's refusal.
 */

import type { ErrorObject } from "ajv";
import {
  set,
  type FieldErrors,
  type FieldPath,
  type FieldValues,
  type Resolver,
  type UseFormSetError,
} from "react-hook-form";

import { placeIn, toBody, validateBody, type Stored } from "@/schema/bodies";

export interface Problem {
  /** Where in the body, as its keys and list positions. Empty for the body as a whole. */
  path: (string | number)[];
  message: string;
}

/** The schema a value failed, where it gives examples of a passing one. */
interface WithExamples {
  examples?: unknown[];
}

/**
 * Ajv states the rule that failed ("must be number,null"). Where the rule
 * has plainer words, or an example, those are given.
 */
function wording(error: ErrorObject): string {
  const [example] = (error.parentSchema as WithExamples).examples ?? [];
  if (error.keyword === "pattern" && example !== undefined) {
    return `Enter this in the form ${String(example)}.`;
  }
  if (error.keyword === "type" && /number|integer/.test(String(error.params.type))) {
    return "Enter a number.";
  }
  if (error.keyword === "minimum") {
    return `Enter ${error.params.limit} or more.`;
  }
  if (error.keyword === "maximum") {
    return `Enter ${error.params.limit} or less.`;
  }
  return error.message ?? "This is not valid.";
}

const isWithin = (inner: Problem, outer: Problem) =>
  inner.path.length > outer.path.length &&
  outer.path.every((part, i) => inner.path[i] === part);

/**
 * Ajv's errors as problems, one per field.
 *
 * Ajv points at the object a required field is missing *from*; a form wants
 * the field itself, so the missing property is appended to the path.
 *
 * It also reports a failure at every level it passes on the way out: a bad
 * number inside an optional part is followed by "must be null" and "must
 * match a schema in anyOf" for the part. The first report for a field is the
 * one about its value, and a part's complaint is explained by the fields
 * inside it, so only those are kept.
 */
export function toProblems(errors: ErrorObject[] | null | undefined): Problem[] {
  const all: Problem[] = (errors ?? [])
    // "must match then schema" only announces the errors that follow it.
    .filter((error) => error.keyword !== "if")
    .map((error) => {
      const path: (string | number)[] = error.instancePath
        .split("/")
        .slice(1)
        .map((part) => (/^\d+$/.test(part) ? Number(part) : part));
      if (error.keyword === "required") {
        path.push(String(error.params.missingProperty));
        return { path, message: "This is required." };
      }
      return { path, message: wording(error) };
    });

  const seen = new Set<string>();
  return all.filter((problem) => {
    const field = fieldName(problem);
    if (seen.has(field) || all.some((other) => isWithin(other, problem))) {
      return false;
    }
    seen.add(field);
    return true;
  });
}

/** react-hook-form's name for a field, or for the form as a whole. */
function fieldName(problem: Problem): string {
  return problem.path.join(".") || "root";
}

/**
 * Check a form's values as the body they would be sent as, on the form's own
 * schedule. The form's field names are the body's, so a problem lands on the
 * field it is about.
 *
 * `also` is for what the schema cannot say, such as one field's value
 * depending on another's. It is given the values and answers with problems.
 */
export const bodyResolver =
  <Values extends FieldValues>(
    name: Stored,
    also: (values: Values) => Problem[] = () => [],
  ): Resolver<Values> =>
  (values) => {
    const validate = validateBody(name);
    validate(toBody(name, values));
    const problems = [
      // Found in the body, and shown on the form, whose rows it may have skipped.
      ...toProblems(validate.errors).map((problem) => ({
        ...problem,
        path: placeIn(name, values, problem.path),
      })),
      ...also(values),
    ];
    if (problems.length === 0) return { values, errors: {} };

    const errors: FieldErrors<Values> = {};
    for (const problem of problems) {
      set(errors, fieldName(problem), { type: "schema", message: problem.message });
    }
    return { values: {}, errors };
  };

/** Show a refused request's problems on the fields they are about. */
export function showProblems<Values extends FieldValues>(
  setError: UseFormSetError<Values>,
  problems: Problem[],
): void {
  for (const problem of problems) {
    setError(fieldName(problem) as FieldPath<Values>, {
      type: "server",
      message: problem.message,
    });
  }
}
