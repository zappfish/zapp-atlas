import { get } from "./client";
import type { Wildtype } from "./types";

/** ZFIN's wild-type lines: the backgrounds a fish can be kept on. */
export const fetchWildtypes = (signal?: AbortSignal) =>
  get<Wildtype[]>("/zfin/wildtypes", signal);
