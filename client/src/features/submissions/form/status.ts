import type { SectionSlug, SectionStatus } from "./sections";
import type { Submission } from "./submission";
import { PUBLISHED_SOURCES } from "./validation";

/**
 * What each section must have before it counts as finished. Images, Control
 * and Phenotype ask for nothing yet, so any value in them finishes them.
 */
const REQUIRED: Record<SectionSlug, (s: Submission) => string[]> = {
  provenance: (s) => [
    s.provenance.sourceType,
    ...(PUBLISHED_SOURCES.includes(s.provenance.sourceType)
      ? [s.provenance.sourceValue]
      : []),
  ],
  images: () => [],
  fish: (s) => [s.fish.strain],
  experiment: (s) => [
    // Only asked for when the rearing was not standard.
    ...(s.experiment.rearing === "Non-standard"
      ? [s.experiment.rearingComment]
      : []),
    ...s.exposures.flatMap((e) => [e.substance, e.route]),
  ],
  control: () => [],
  phenotype: () => [],
};

/** Everything a section holds, to tell an untouched one from a started one. */
const VALUES: Record<SectionSlug, (s: Submission) => unknown[]> = {
  provenance: (s) => Object.values(s.provenance),
  images: (s) => s.images.flatMap((i) => Object.values(i)),
  fish: (s) => Object.values(s.fish),
  experiment: (s) => [
    ...Object.values(s.experiment),
    ...s.exposures.flatMap((e) => Object.values(e)),
  ],
  control: (s) => s.controls.flatMap((c) => Object.values(c)),
  phenotype: (s) => s.observations.flatMap((o) => Object.values(o)),
};

const filled = (value: unknown): boolean =>
  Array.isArray(value)
    ? value.length > 0
    : value instanceof FileList
      ? value.length > 0
      : typeof value === "string"
        ? value.trim() !== ""
        : value != null;

export const sectionStatus = (
  slug: SectionSlug,
  submission: Submission,
  /** The defaults a section starts with, which are not answers. */
  untouched: Submission,
): SectionStatus => {
  const defaults = new Set(VALUES[slug](untouched).filter(filled));
  const answered = VALUES[slug](submission).filter(
    (value) => filled(value) && !defaults.has(value),
  );

  if (answered.length === 0) return "not-started";
  return REQUIRED[slug](submission).every(filled) ? "complete" : "in-progress";
};
