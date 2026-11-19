import type { Body } from "@/schema/bodies";
import type { SectionSlug, SectionStatus } from "./sections";

const filled = (text: string | null | undefined) =>
  text != null && text.trim() !== "";

/**
 * Where each section of the experiment page stands, from what the setup form
 * holds and how many exposure events have been saved.
 */
export const sectionStatuses = (
  experiment: Body<"Experiment">,
  exposureEvents: number,
): Record<SectionSlug, SectionStatus> => ({
  fish: experiment.fish ? "complete" : "not-started",
  experiment:
    experiment.standard_rearing_condition == null
      ? "not-started"
      : // Only asked for when the rearing was not standard.
        experiment.standard_rearing_condition ||
          filled(experiment.rearing_condition_comment)
        ? "complete"
        : "in-progress",
  control: (experiment.control ?? []).some((control) =>
    filled(control.control_type),
  )
    ? "complete"
    : "not-started",
  exposures: exposureEvents > 0 ? "complete" : "not-started",
});
