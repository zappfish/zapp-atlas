/**
 * The generated read JSON Schema (`./schema.json`), typed once as a
 * `JSONSchemaDocument` so callers don't each re-cast the raw import.
 *
 * Pass it to `makeEmpty`, `compile`, or the `toInputSchema`/`toDraftSchema`
 * transforms.
 */

import rawSchema from "./schema.json";
import type { JSONSchemaDocument } from "./variants";

export const schemaDocument = rawSchema as unknown as JSONSchemaDocument;
