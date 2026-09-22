/**
 * Response types and fetches for the group dashboard.
 *
 * Separate from the generated types in ../schema: those model the database and
 * carry `research_group`, which these nested routes take from the path. Mirrors
 * api/dto.py.
 *
 * Caching and loading state belong to the useQuery hooks in ./queries.
 */

/** ISO-8601 string. */
type Timestamp = string;

interface Audited {
  created_at: Timestamp | null;
  updated_at: Timestamp | null;
}

export interface Group {
  id: number;
  name: string;
}

export interface Member extends Audited {
  id: number;
  /** An ORCID CURIE: "ORCID:0000-0002-1825-0097". */
  member: string;
  role: "admin" | "member";
}

export interface FishTankEntry extends Audited {
  id: number;
  fish: { zfin_id: string; name: string };
}

export interface CabinetEntry extends Audited {
  id: number;
  chemical_id: string;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const get = async <T,>(path: string, signal?: AbortSignal): Promise<T> => {
  // Same origin, so the session cookie is sent automatically.
  const res = await fetch(`/api${path}`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!res.ok) {
    // Non-members get 404, not 403, so group ids can't be probed.
    throw new ApiError(res.status, `GET /api${path} failed (${res.status})`);
  }
  return (await res.json()) as T;
};

export const fetchGroups = (signal?: AbortSignal) =>
  get<Group[]>("/research-groups", signal);

export const fetchGroup = (groupId: number, signal?: AbortSignal) =>
  get<Group>(`/research-groups/${groupId}`, signal);

export const fetchMembers = (groupId: number, signal?: AbortSignal) =>
  get<Member[]>(`/research-groups/${groupId}/members`, signal);

export const fetchFishTank = (groupId: number, signal?: AbortSignal) =>
  get<FishTankEntry[]>(`/research-groups/${groupId}/fish-tank`, signal);

export const fetchCabinet = (groupId: number, signal?: AbortSignal) =>
  get<CabinetEntry[]>(`/research-groups/${groupId}/chemical-cabinet`, signal);
