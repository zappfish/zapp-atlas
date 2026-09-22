/**
 * Mock data shaped like the /api responses, so the layout can be built before
 * the fetches are wired. Delete once they are.
 */

export interface Group {
  id: number;
  name: string;
}

export interface Member {
  id: number;
  /** An ORCID CURIE, as the API returns it. */
  member: string;
  role: "admin" | "member";
}

export interface FishTankEntry {
  id: number;
  fish: { zfin_id: string; name: string };
}

export interface CabinetEntry {
  id: number;
  chemical_id: string;
}

/** Not in the schema yet; the set the Jinja filter tabs assume. */
export const STATUSES = [
  "Published",
  "In Progress",
  "On Hold",
  "Retracted",
] as const;

export type Status = (typeof STATUSES)[number];

export interface Submission {
  id: number;
  title: string;
  status: Status;
  /** The submitter's display name. */
  submittedBy: string;
  /** Last updated, preformatted until the API returns a date to format. */
  date: string;
}

export interface Dashboard {
  groups: Group[];
  group: Group;
  isAdmin: boolean;
  members: Member[];
  fishTank: FishTankEntry[];
  cabinet: CabinetEntry[];
  submissions: Submission[];
}

export const PLACEHOLDER: Dashboard = {
  groups: [
    { id: 1, name: "Bhandari Lab" },
    { id: 2, name: "Neurotox Lab" },
    { id: 3, name: "Zebrafish Core" },
  ],
  group: { id: 1, name: "Bhandari Lab" },
  // Not in any API response; will be derived from the members list.
  isAdmin: true,
  members: [
    { id: 1, member: "ORCID:0000-0002-1825-0097", role: "admin" },
    { id: 2, member: "ORCID:0000-0001-5109-3700", role: "member" },
  ],
  fishTank: [
    { id: 1, fish: { zfin_id: "ZFIN:ZDB-GENO-960809-7", name: "AB" } },
    { id: 2, fish: { zfin_id: "ZFIN:ZDB-GENO-070102-5", name: "TU" } },
    { id: 3, fish: { zfin_id: "ZFIN:ZDB-GENO-990623-2", name: "WIK" } },
  ],
  cabinet: [
    { id: 1, chemical_id: "CHEBI:16236" },
    { id: 2, chemical_id: "CHEBI:33216" },
  ],
  submissions: [
    {
      id: 1,
      title: "Ethanol exposure, 24 hpf",
      status: "Published",
      submittedBy: "Josiah Carberry",
      date: "Mar 4, 2026",
    },
    {
      id: 2,
      title: "BPA dose response in AB",
      status: "In Progress",
      submittedBy: "Ada Lovelace",
      date: "Mar 1, 2026",
    },
    {
      id: 3,
      title: "Cadmium co-exposure pilot",
      status: "On Hold",
      submittedBy: "Josiah Carberry",
      date: "Feb 18, 2026",
    },
  ],
};
