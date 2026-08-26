/**
 * Blank-instance factory + immutable deep-update helper for form state.
 *
 * `makeEmpty` builds a blank entry from the generated JSON Schema, so the empty
 * shape is never hand-maintained. Recommended usage (see the docs): the *form
 * root* calls `makeEmpty` once for a single root instance and passes slices +
 * `updateAt` down; leaf components don't each call it. `makeEmpty` is also how
 * you append a nested row ("Add experiment" → `makeEmpty(schema, "Experiment")`).
 *
 * Value policy (kept deliberately simple; adjust here if needed):
 *   - multivalued slots      → `[]`
 *   - string scalars         → `""`  (convenient for controlled inputs)
 *   - everything else        → omitted (numbers, booleans, enums, and nested
 *                              single objects stay unset until the user fills /
 *                              opens them)
 */

import type { Draft } from "./types";
import type { JSONSchemaDocument } from "./variants";

interface SchemaProp {
  type?: string | string[];
  [key: string]: unknown;
}

function typesOf(prop: SchemaProp): string[] {
  if (Array.isArray(prop.type)) return prop.type;
  if (typeof prop.type === "string") return [prop.type];
  return [];
}

/** Empty value for a property, or `undefined` to omit the key entirely. */
function emptyValue(prop: SchemaProp): unknown {
  const types = typesOf(prop);
  if (types.includes("array")) return [];
  if (types.includes("string")) return "";
  return undefined;
}

/**
 * Build a blank instance of `defName` from the schema document. Returns a
 * `Draft<T>` (deeply optional) — it will not pass input validation until
 * required fields are filled, which is the point.
 */
export function makeEmpty<T = unknown>(
  schema: JSONSchemaDocument,
  defName: string,
): Draft<T> {
  const def = schema.$defs?.[defName];
  const properties = (def?.properties ?? {}) as Record<string, SchemaProp>;

  const out: Record<string, unknown> = {};
  for (const [name, prop] of Object.entries(properties)) {
    const value = emptyValue(prop);
    if (value !== undefined) out[name] = value;
  }
  return out as Draft<T>;
}

export type PathKey = string | number;

/**
 * Immutably set `value` at `path` within `root`, cloning along the path. Returns
 * a new root; `root` is unchanged. Powers the "one empty root, deeply updated"
 * form-state pattern — a leaf `onChange` calls `updateAt(root, path, next)`.
 */
export function updateAt<T>(
  root: T,
  path: readonly PathKey[],
  value: unknown,
): T {
  if (path.length === 0) return value as T;
  const [head, ...rest] = path as [PathKey, ...PathKey[]];
  const base: Record<PathKey, unknown> = Array.isArray(root)
    ? ([...(root as unknown[])] as unknown as Record<PathKey, unknown>)
    : ({ ...(root as object) } as Record<PathKey, unknown>);
  base[head] = updateAt(base[head], rest, value);
  return base as unknown as T;
}
