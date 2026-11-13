/** The nested routes take `research_group` from the path, so it is not a field. */

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
  /** Absent until the response carries it; a member who has never signed in
   *  has no name to carry either. */
  name?: string | null;
  role: ResearchGroupRole;
}

export type ResearchGroupRole = "admin" | "member";

export interface FishTankEntry extends Audited {
  id: number;
  fish: { zfin_id: string; name: string };
}

export interface CabinetEntry extends Audited {
  id: number;
  chemical_id: string;
  /** What the group calls it, e.g. "BPA stock". Unique within the group. */
  nickname?: string | null;
}

export interface Study {
  id: number;
  research_group: number | null;
  /** "PMID:…" or "DOI:…"; absent while unpublished. */
  publication: string | null;
  nickname: string | null;
  description: string | null;
}
