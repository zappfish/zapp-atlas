/**
 * Runtime validation + type-safe unmarshalling, driven by the generated JSON
 * Schema (`./schema.json`) via Ajv.
 *
 * The same compiled validator serves both boundaries:
 *   - outgoing: validate a create/update payload before POST/PATCH (`allErrors`
 *     gives every field problem at once, for inline form feedback);
 *   - incoming: validate a server response — an Ajv validator is a TypeScript
 *     type guard (`data is T`), so a successful check narrows `unknown → T`
 *     with a runtime guarantee (no unchecked `as` cast).
 *
 * We ship ONE reference validator here (Study, a top-level container). Because
 * JSON Schema resolves `$ref`s, validating a Study validates its whole nested
 * tree. Add more entities the same way, as components need them — see
 * `client/src/schema/README.md`.
 */

import Ajv2019 from "ajv/dist/2019";
import type { ErrorObject, ValidateFunction } from "ajv";

import { schemaDocument } from "./document";
import type { Study } from "./index";
import type { Create } from "./types";
import { toInputSchema, type JSONSchemaDocument } from "./variants";

// strict:false — the LinkML output carries annotation keywords ($comment, title,
// version, metamodel_version) and multi-type ("array"|"null") slots that Ajv's
// strict mode would reject. allErrors:true so one validate() call reports every
// field problem.
const ajv = new Ajv2019({ allErrors: true, strict: false });

/**
 * Compile a validator for a single entity within the bundled schema document.
 * The generic `T` pairs a `$defs` entry with its generated TypeScript type;
 * both come from the same LinkML source, so the pairing can't drift.
 */
export function compile<T>(
  doc: JSONSchemaDocument,
  defName: string,
): ValidateFunction<T> {
  return ajv.compile<T>({ $defs: doc.$defs, $ref: `#/$defs/${defName}` });
}

/** Thrown by {@link parseAs} when data does not match its schema. */
export class SchemaValidationError extends Error {
  constructor(readonly errors: ErrorObject[]) {
    super(`Payload did not match schema (${errors.length} error(s))`);
    this.name = "SchemaValidationError";
  }
}

/**
 * Validate `data` and return it narrowed to `T`, throwing on failure —
 * Zod `.parse()`-style ergonomics. Use to unmarshal server responses.
 */
export function parseAs<T>(validate: ValidateFunction<T>, data: unknown): T {
  if (!validate(data)) {
    throw new SchemaValidationError(validate.errors ?? []);
  }
  return data;
}

// --- Reference validators: Study --------------------------------------------

/** Validate a Study read from the API (`id` present); narrows `unknown → Study`. */
export const validateStudy: ValidateFunction<Study> = compile<Study>(
  schemaDocument,
  "Study",
);

/** Validate a Study create payload (`id`s omitted) before POSTing. */
export const validateStudyInput: ValidateFunction<Create<Study>> = compile<
  Create<Study>
>(toInputSchema(schemaDocument), "Study");
