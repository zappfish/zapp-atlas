/**
 * Derive schema flavours from the single generated read JSON Schema
 * (`./schema.json`) at runtime — no separate generated files.
 *
 * Every entity constraint lives in the document's `$defs` (nested references are
 * `$ref`s into `$defs`), so relaxing a def's `required` list cascades to every
 * place that entity is used.
 *
 *   - read   → the generated schema as-is (server responses; `id` present).
 *   - input  → `id` dropped from every `required` (POST/PATCH payloads).
 *   - draft  → all `required` dropped (in-progress entries; deferred use).
 */

export interface JSONSchemaDef {
  required?: string[];
  [key: string]: unknown;
}

export interface JSONSchemaDocument {
  $defs?: Record<string, JSONSchemaDef>;
  [key: string]: unknown;
}

/**
 * Return a copy of `schema` where each `$defs` entry keeps only the required
 * fields for which `keep(field)` is true. Empty `required` arrays are removed.
 */
function transformRequired(
  schema: JSONSchemaDocument,
  keep: (field: string) => boolean,
): JSONSchemaDocument {
  const defs = schema.$defs ?? {};
  const nextDefs: Record<string, JSONSchemaDef> = {};

  for (const [name, def] of Object.entries(defs)) {
    if (!Array.isArray(def.required)) {
      nextDefs[name] = def;
      continue;
    }
    const required = def.required.filter(keep);
    if (required.length > 0) {
      nextDefs[name] = { ...def, required };
    } else {
      const clone = { ...def };
      delete clone.required;
      nextDefs[name] = clone;
    }
  }

  return { ...schema, $defs: nextDefs };
}

/** POST/PATCH payloads: `id` is server-generated, so drop it from `required`. */
export function toInputSchema(schema: JSONSchemaDocument): JSONSchemaDocument {
  return transformRequired(schema, (field) => field !== "id");
}

/** In-progress drafts: nothing is required (deferred — not wired up yet). */
export function toDraftSchema(schema: JSONSchemaDocument): JSONSchemaDocument {
  return transformRequired(schema, () => false);
}
