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
import { toInputSchema } from "./variants";

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
  const validator = validators.get(name) ?? compile(inputSchema, name);
  validators.set(name, validator);
  return validator as ValidateFunction<Body<Class>>;
}

// -- reading the schema ------------------------------------------------------

/** A property of a class, as JSON Schema writes it. */
interface Property {
  readOnly?: boolean;
  $ref?: string;
  anyOf?: Property[];
  items?: Property;
}

/** A slot of a class: what the rest of this file needs to know of a property. */
interface Slot {
  key: string;
  /** Set by the server, so a body does not carry it. */
  readOnly: boolean;
  /** The class the slot holds, singly or in a list. Undefined for a plain value. */
  holds: string | undefined;
}

const definitions = schemaDocument.$defs as Record<
  string,
  { properties?: Record<string, Property> }
>;

/**
 * The class a property refers to, directly, as a list's items, or as one
 * side of an optional value. An enum is referred to the same way, and is told
 * apart by having no properties of its own.
 */
function classHeld(property: Property): string | undefined {
  const ref = [property, property.items, ...(property.anyOf ?? [])].find(
    (each) => each?.$ref,
  )?.$ref;
  const name = ref?.replace("#/$defs/", "");
  return name !== undefined && definitions[name]?.properties ? name : undefined;
}

/** A class's slots, in the schema's order. */
function slotsOf(className: string): Slot[] {
  return Object.entries(definitions[className]?.properties ?? {}).map(
    ([key, property]) => ({
      key,
      readOnly: property.readOnly === true,
      holds: classHeld(property),
    }),
  );
}

// -- making a body -----------------------------------------------------------

type Fields = Record<string, unknown>;

/** Is there nothing here for a body to say? */
const isBlank = (value: unknown) =>
  value == null ||
  (Array.isArray(value) && value.length === 0) ||
  (typeof value === "string" && value.trim() === "") ||
  (typeof value === "number" && Number.isNaN(value));

/**
 * Throws when `value` has a key the class has no slot for. That is a form
 * field named for something other than the schema's slot, which is a mistake
 * in the form and not something a user typed.
 */
function checkKeys(className: string, value: Fields, slots: Slot[]): void {
  const unknown = Object.keys(value).find(
    (key) => !slots.some((slot) => slot.key === key),
  );
  if (unknown !== undefined) {
    throw new Error(`${className} has no slot named ${unknown}`);
  }
}

/**
 * What a body says of one instance of a class: its slots in the schema's
 * order, without those the server sets and those left blank. The same is
 * done to every class nested in it.
 *
 * An instance with nothing filled in comes back as `{}`.
 */
function prune(className: string, value: Fields): Fields {
  const slots = slotsOf(className);
  checkKeys(className, value, slots);

  const body: Fields = {};
  for (const slot of slots) {
    if (slot.readOnly) continue;
    const held = value[slot.key];
    const said = slot.holds === undefined ? held : pruneHeld(slot.holds, held);
    if (!isBlank(said)) body[slot.key] = said;
  }
  return body;
}

/**
 * What a body says of a slot that holds a class: the rows that say
 * something, or the one instance if it says something, or nothing.
 */
function pruneHeld(className: string, held: unknown): unknown {
  if (isBlank(held)) return undefined;
  if (Array.isArray(held)) {
    return filledRows(className, held).map(({ row }) => row);
  }
  const instance = prune(className, held as Fields);
  return Object.keys(instance).length > 0 ? instance : undefined;
}

/**
 * The rows of a list that say something, pruned, each with its position in
 * the list it came from. A row with nothing filled in is not in a body.
 */
function filledRows(
  className: string,
  rows: Fields[],
): { index: number; row: Fields }[] {
  return rows
    .map((row, index) => ({ index, row: prune(className, row) }))
    .filter(({ row }) => Object.keys(row).length > 0);
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
  return prune(name, value as Fields) as Body<Class>;
}

type Path = (string | number)[];

/**
 * Where in `value` a place in its body is.
 *
 * A body leaves out rows with nothing filled in, so its third row may be the
 * form's fourth. A problem found in the body is shown on the form, and has
 * to be counted in the form's rows.
 */
export function placeIn(name: Stored, value: object, bodyPath: Path): Path {
  return placeWithin(name, value, bodyPath);
}

/**
 * `placeIn`, one step of the path at a time. `className` is the class
 * `value` is an instance or a list of, and is undefined once the path has
 * gone into a plain value.
 */
function placeWithin(
  className: string | undefined,
  value: unknown,
  [key, ...rest]: Path,
): Path {
  if (key === undefined) return [];

  if (typeof key === "number") {
    // The body's row `key` is the form's row `index`.
    const rows = value as Fields[];
    const index =
      className === undefined
        ? key
        : (filledRows(className, rows)[key]?.index ?? key);
    return [index, ...placeWithin(className, rows[index], rest)];
  }

  const slot =
    className === undefined
      ? undefined
      : slotsOf(className).find((each) => each.key === key);
  return [key, ...placeWithin(slot?.holds, (value as Fields)[key], rest)];
}

/** Do two values make the same body? Whether a form has anything to save. */
export function sameBody(name: Stored, one: object, other: object): boolean {
  return (
    JSON.stringify(toBody(name, one)) === JSON.stringify(toBody(name, other))
  );
}
