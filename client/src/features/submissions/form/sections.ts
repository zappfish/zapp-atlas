/** The form's sections, in the order they are filled. */
export const SECTIONS = [
  { slug: "images", label: "Images" },
  { slug: "provenance", label: "Provenance" },
  { slug: "fish", label: "Fish Information" },
  { slug: "experiment", label: "Experiment Information" },
  { slug: "control", label: "Control" },
  { slug: "phenotype", label: "Phenotype Observation" },
] as const;

export type SectionSlug = (typeof SECTIONS)[number]["slug"];

/**
 * Where a section stands. Derived from its fields once they exist; the rail
 * and the section headers read it, and nothing else decides it.
 */
export type SectionStatus =
  | "not-started"
  | "in-progress"
  | "complete"
  | "has-errors";

export const STATUS_LABELS: Record<SectionStatus, string> = {
  complete: "Complete",
  "in-progress": "In progress",
  "not-started": "Not started",
  "has-errors": "Has errors",
};
