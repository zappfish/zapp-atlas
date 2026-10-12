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

/**
 * The sources the server accepts — chem/normalize.py NAMESPACES, whose two
 * casing aliases collapse to one entry each. Order sets the menu, and the
 * first is the default.
 */
export const ID_TYPES = [
  { id: "CHEBI", label: "ChEBI", example: "27732" },
  { id: "PUBCHEM.COMPOUND", label: "PubChem", example: "2519" },
  { id: "CAS", label: "CAS", example: "58-08-2" },
  { id: "INCHIKEY", label: "InChIKey", example: "RYYVLZVUVIJVGH-UHFFFAOYSA-N" },
  { id: "HMDB", label: "HMDB", example: "HMDB0001847" },
  { id: "CHEMBL.COMPOUND", label: "ChEMBL", example: "CHEMBL113" },
  { id: "UNII", label: "UNII", example: "3G6A5W338E" },
  { id: "MESH", label: "MeSH", example: "D002110" },
  { id: "UMLS", label: "UMLS", example: "C0006644" },
  { id: "DrugCentral", label: "DrugCentral", example: "471" },
  { id: "GTOPDB", label: "GtoPdb", example: "407" },
  { id: "RXCUI", label: "RxCUI", example: "1886" },
  { id: "DRUGBANK", label: "DrugBank", example: "DB00201" },
  { id: "KEGG.COMPOUND", label: "KEGG", example: "C07481" },
  { id: "UniProtKB", label: "UniProtKB", example: "P12345" },
  { id: "ENSEMBL", label: "Ensembl", example: "ENSG00000139618" },
  { id: "PR", label: "Protein Ontology", example: "P12345" },
] as const;

export type IdType = (typeof ID_TYPES)[number];

/** By id, for the chosen source's label and example. */
export const idTypeOf = (id: string): IdType | undefined =>
  ID_TYPES.find((each) => each.id === id);

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
