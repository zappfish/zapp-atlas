/**
 * Working with ZFIN's developmental stages, which the server serves with the
 * hours post fertilization each covers (`useStages`). A stage runs from its
 * `start_hours` up to, not including, its `end_hours`.
 */

import type { Stage } from "@/api/types";

export const STAGE_UNITS = ["hpf", "dpf", "month"];

const HOURS_PER: Record<string, number> = { hpf: 1, dpf: 24, month: 30 * 24 };

/** Hours post fertilization; null unless `value` is a number. */
export const toHours = (value: string, unit: string): number | null => {
  const text = value.trim();
  const per = HOURS_PER[unit];
  if (!/^\d+(\.\d+)?$/.test(text) || per === undefined) return null;
  return Number(text) * per;
};

/** The stage a time falls in. */
export const stageAt = (
  stages: Stage[],
  value: string,
  unit: string,
): Stage | undefined => {
  const hours = toHours(value, unit);
  if (hours === null) return undefined;
  return stages.find(
    (stage) => hours >= stage.start_hours && hours < stage.end_hours,
  );
};

/** The hours a stage covers, as a card's title gives them. */
export const stageSpan = (stage: Stage) =>
  `${stage.start_hours} to ${stage.end_hours} hpf`;
