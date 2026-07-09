/**
 * Generic type helpers for working with the LinkML-generated entity types in
 * `./index`.
 *
 * The generated interfaces describe the *read* shape of an entity (every
 * `ZappEntity` has a server-assigned `id`). Rather than materialise a separate
 * Create/Update/Draft interface for every entity, we derive those shapes with
 * these generic utilities:
 *
 *   - `Create<T>`  payloads you POST to the API: `id` is server-generated, so it
 *                  is optional at *every* level of nesting (a new Study with new
 *                  nested Experiments carries no ids yet). Other required fields
 *                  stay required.
 *   - `Update<T>`  PATCH payloads: a shallow partial (top-level fields optional).
 *   - `Draft<T>`   in-progress editing state: everything optional, at every level.
 */

/** Recursively make `id` optional wherever it appears. */
type IdOptional<T> = "id" extends keyof T ? Omit<T, "id"> & { id?: T["id"] } : T;

/** POST payload: `id` optional at every level; other required fields preserved. */
export type Create<T> = T extends readonly (infer U)[]
  ? Create<U>[]
  : T extends object
    ? IdOptional<{ [K in keyof T]: Create<T[K]> }>
    : T;

/** PATCH payload: a shallow partial of the entity. */
export type Update<T> = Partial<T>;

/** Deeply-optional shape: everything optional at every level of nesting. */
export type DeepPartial<T> = T extends readonly (infer U)[]
  ? DeepPartial<U>[]
  : T extends object
    ? { [K in keyof T]?: DeepPartial<T[K]> }
    : T;

/** In-progress editing state (an unfinished entry). */
export type Draft<T> = DeepPartial<T>;
