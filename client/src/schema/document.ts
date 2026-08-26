/**
 * The generated read JSON Schema (`./schema.json`), typed once as a
 * `JSONSchemaDocument` and normalised so callers don't each re-cast/repair the
 * raw import.
 *
 * `normalizeNullableRefs` compensates for a LinkML generator quirk (optional
 * enum slots emitted non-nullable); see `./variants`. Pass this to `makeEmpty`,
 * `compile`, or the `toInputSchema`/`toDraftSchema` transforms — not the raw
 * `schema.json`.
 */

import rawSchema from "./schema.json";
import { normalizeNullableRefs, type JSONSchemaDocument } from "./variants";

export const schemaDocument = normalizeNullableRefs(
  rawSchema as unknown as JSONSchemaDocument,
);
