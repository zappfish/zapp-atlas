/**
 * Type helpers for working with the LinkML-generated entity types in `./index`.
 *
 * The generated interfaces describe the *read* shape of an entity. What the
 * API accepts for one is `Body<Class>` in `./bodies`, which comes from the
 * server's OpenAPI document. `Draft<T>` is for a form's state, where anything
 * may still be missing.
 */

/** Deeply-optional shape: everything optional at every level of nesting. */
export type DeepPartial<T> = T extends readonly (infer U)[]
  ? DeepPartial<U>[]
  : T extends object
    ? { [K in keyof T]?: DeepPartial<T[K]> }
    : T;

/** In-progress editing state (an unfinished entry). */
export type Draft<T> = DeepPartial<T>;
