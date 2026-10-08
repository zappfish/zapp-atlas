/** A suggestion carries only a name and its ChEBI ids; the record is a second call. */

import { get, send } from "./client";

export interface Suggestion {
  name: string;
  chebi_ids: string[];
}

export interface EquivalentIdentifier {
  identifier: string | null;
  label: string | null;
  description: string | null;
}

export interface Chemical {
  normalized: boolean;
  primary_id: string | null;
  label: string | null;
  description: string | null;
  biolink_type: string[] | null;
  equivalent_identifiers: EquivalentIdentifier[];
}

/** The sources the server accepts — chem/normalize.py NAMESPACES. */
export const ID_TYPES = [
  "CHEBI",
  "PUBCHEM.COMPOUND",
  "CAS",
  "INCHIKEY",
  "HMDB",
  "CHEMBL.COMPOUND",
  "UNII",
  "MESH",
  "UMLS",
  "DrugCentral",
  "GTOPDB",
  "RXCUI",
  "DRUGBANK",
  "KEGG.COMPOUND",
  "UniProtKB",
  "ENSEMBL",
  "PR",
] as const;

/** Database names rather than prefixes. */
export const ID_TYPE_LABELS: Record<string, string> = {
  CHEBI: "ChEBI",
  "PUBCHEM.COMPOUND": "PubChem",
  CAS: "CAS",
  INCHIKEY: "InChIKey",
  HMDB: "HMDB",
  "CHEMBL.COMPOUND": "ChEMBL",
  UNII: "UNII",
  MESH: "MeSH",
  UMLS: "UMLS",
  DrugCentral: "DrugCentral",
  GTOPDB: "GtoPdb",
  RXCUI: "RxCUI",
  DRUGBANK: "DrugBank",
  "KEGG.COMPOUND": "KEGG",
  UniProtKB: "UniProtKB",
  ENSEMBL: "Ensembl",
  PR: "Protein Ontology",
};

/** The prefix is optional: the type is already chosen. */
export const toCurie = (idType: string, id: string): string | null => {
  const bare = id.trim().replace(new RegExp(`^${idType}:`, "i"), "");
  return bare ? `${idType}:${bare}` : null;
};

export const searchChemicals = (q: string, signal?: AbortSignal) =>
  get<Suggestion[]>(
    `/chemicals/autocomplete?q=${encodeURIComponent(q)}&limit=8`,
    signal,
    "Could not search chemicals",
  );

/** The record behind a suggestion. */
export const normalizeChemical = async (
  chebiId: string,
  signal?: AbortSignal,
): Promise<Chemical> => {
  const [namespace, id] = chebiId.split(":");
  // `results` holds every match; `result` is the one the server settled on.
  const body = await send<{ result: Chemical }>(
    "POST",
    "/chemicals/normalize",
    { namespace, chemical_id: id },
    signal,
  );
  return body!.result;
};
