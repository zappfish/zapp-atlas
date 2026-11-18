import { get, send } from "./client";
import type {
  FishDescription,
  FishResolution,
  Wildtype,
  ZfinAlleleSearch,
} from "./types";

/** ZFIN's wild-type lines: the backgrounds a fish can be kept on. */
export const fetchWildtypes = (signal?: AbortSignal) =>
  get<Wildtype[]>("/zfin/wildtypes", signal);

/** Alleles matching a symbol, gene symbol or construct name, best first. */
export const searchAlleles = (q: string, signal?: AbortSignal) =>
  get<ZfinAlleleSearch>(
    `/zfin/alleles?q=${encodeURIComponent(q)}&limit=12`,
    signal,
  );

/**
 * The registered ZFIN genotype and fish a description corresponds to. A
 * POST, since a description does not fit in a URL, but a read: the answer
 * depends only on the description and the bundle, so it is cached.
 */
export const resolveFish = async (
  description: FishDescription,
  signal?: AbortSignal,
): Promise<FishResolution> => {
  const found = await send<FishResolution>("POST", "/zfin/resolve", description, signal);
  if (found === null) throw new Error("ZFIN gave no answer");
  return found;
};
