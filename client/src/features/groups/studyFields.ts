import type { Study, StudyBody } from "@/api/types";
import { toBody } from "@/schema/bodies";

/** The study's own fields as a body. Its experiments are saved on their own. */
export const ownFields = (study: Study): StudyBody =>
  toBody("Study", { ...study, experiment: undefined });
