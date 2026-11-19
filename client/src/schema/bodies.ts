/**
 * Request bodies: what the API accepts for a class, as opposed to what it
 * returns.
 *
 * `schema.json` describes each class as it is read back. A body differs in
 * what it leaves out: the row's `id`, the slots the server sets, and the
 * level beneath it, which is saved through its own routes. The first two are
 * marked `readOnly` in the schema; a page takes the third out itself, since
 * it is what the page lists.
 *
 * The body types come from the server's OpenAPI document, so the compiler
 * refuses a field the API would. The checks here are for a form to show a
 * problem before the request is sent; the server decides.
 */

import type { ValidateFunction } from "ajv";

import type { components } from "@/api/openapi";

import { schemaDocument } from "./document";
import { compile } from "./validation";
import { toInputSchema, type JSONSchemaDef } from "./variants";

type Schemas = components["schemas"];

/** The classes the API takes bodies for: each has a `<Class>Input` model. */
export type Stored = {
  [Name in keyof Schemas]: Name extends `${infer Class}Input` ? Class : never;
}[keyof Schemas];

/** The body the API accepts for a class. */
export type Body<Class extends Stored> = Schemas[`${Class}Input`];

const inputSchema = toInputSchema(schemaDocument);
const validators = new Map<Stored, ValidateFunction>();

/**
 * The validator for a class's body: every constraint the schema puts on the
 * class, without requiring the `id` only a stored row has.
 */
export function validateBody<Class extends Stored>(
  name: Class,
): ValidateFunction<Body<Class>> {
  const made = validators.get(name) ?? compile(inputSchema, name);
  validators.set(name, made);
  return made as ValidateFunction<Body<Class>>;
}

interface Declared {
  readOnly?: boolean;
  $ref?: string;
  anyOf?: Declared[];
  items?: Declared;
}

const definitions = schemaDocument.$defs as Record<string, JSONSchemaDef>;

/**
 * The class a property holds, when it holds one, singly or in a list. An enum
 * is referred to the same way, and is told apart by having no properties.
 */
function classOf(declared: Declared): string | undefined {
  const ref = [declared, declared.items, ...(declared.anyOf ?? [])].find(
    (each) => each?.$ref,
  )?.$ref;
  const name = ref?.replace("#/$defs/", "");
  return name !== undefined && definitions[name]?.properties ? name : undefined;
}

const isBlank = (value: unknown) =>
  value == null ||
  (Array.isArray(value) && value.length === 0) ||
  (typeof value === "string" && value.trim() === "") ||
  (typeof value === "number" && Number.isNaN(value));

function carried(defName: string, value: object): Record<string, unknown> {
  const properties = definitions[defName]?.properties as Record<string, Declared>;

  const unknown = Object.keys(value).find((key) => !(key in properties));
  if (unknown !== undefined) {
    throw new Error(`${defName} has no slot named ${unknown}`);
  }

  // In the schema's order, so two bodies that say the same thing are written
  // the same way.
  const body: Record<string, unknown> = {};
  for (const [key, declared] of Object.entries(properties)) {
    const held = (value as Record<string, unknown>)[key];
    if (declared.readOnly || isBlank(held)) continue;

    const nested = classOf(declared);
    if (nested === undefined) {
      body[key] = held;
    } else if (Array.isArray(held)) {
      // A row with nothing filled in is a row that is not there, and a list
      // with no rows is a list that is not there.
      const rows = held
        .map((item: object) => carried(nested, item))
        .filter((item) => Object.keys(item).length > 0);
      if (rows.length > 0) body[key] = rows;
    } else {
      const part = carried(nested, held as object);
      // A part with nothing filled in is a part that is not there.
      if (Object.keys(part).length > 0) body[key] = part;
    }
  }
  return body;
}

/**
 * The body that says what `value` says: a record as it was read, or a form's
 * state. Left out, at every depth, are what the server sets and what is
 * blank, which a body says by omission.
 *
 * `value` must not hold the level beneath the class; the result would then
 * not be a body.
 */
export function toBody<Class extends Stored>(
  name: Class,
  value: object,
): Body<Class> {
  return carried(name, value) as Body<Class>;
}

/**
 * Where in `value` a place in its body is.
 *
 * A body leaves out rows with nothing filled in, so its third row may be the
 * form's fourth. A problem found in the body is shown on the form, and has
 * to be counted in the form's rows.
 */
export function placeIn(
  name: Stored,
  value: object,
  bodyPath: (string | number)[],
): (string | number)[] {
  let defName: string | undefined = name;
  let held: unknown = value;

  return bodyPath.map((key) => {
    const className = defName;
    if (typeof key === "number" && Array.isArray(held) && className) {
      const kept = held.flatMap((row: object, index) =>
        Object.keys(carried(className, row)).length > 0 ? [index] : [],
      );
      const index = kept[key] ?? key;
      held = held[index];
      return index;
    }
    const declared: Declared | undefined =
      className === undefined
        ? undefined
        : (definitions[className]?.properties as Record<string, Declared>)[key];
    defName = declared && classOf(declared);
    held = (held as Record<string, unknown> | undefined)?.[key];
    return key;
  });
}

/** Do two values make the same body? Whether a form has anything to save. */
export function sameBody(name: Stored, one: object, other: object): boolean {
  return (
    JSON.stringify(toBody(name, one)) === JSON.stringify(toBody(name, other))
  );
}
