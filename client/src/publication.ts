/** A study's publication identifier, as Study.publication stores it. */

export type PublicationType = "PMID" | "DOI";

export const PUBLICATION_TYPES: PublicationType[] = ["PMID", "DOI"];

export const isPublicationType = (type: string): type is PublicationType =>
  (PUBLICATION_TYPES as string[]).includes(type);

const PMID = /^(?:PMID:\s*)?(\d+)$/i;
const DOI = /^(?:doi:\s*|https?:\/\/(?:dx\.)?doi\.org\/)?(10\.\d{4,9}\/\S+)$/i;

export const PUBLICATION_HINTS: Record<
  PublicationType,
  { example: string; message: string }
> = {
  PMID: { example: "41812223", message: "Enter a PubMed ID, e.g. 41812223." },
  DOI: { example: "10.1000/xyz123", message: "Enter a DOI, e.g. 10.1000/xyz123." },
};

/** The stored CURIE, e.g. "PMID:41812223"; null if the text is not one. */
export const toPublication = (
  type: PublicationType,
  text: string,
): string | null => {
  const match = (type === "PMID" ? PMID : DOI).exec(text.trim());
  return match ? `${type}:${match[1]}` : null;
};
