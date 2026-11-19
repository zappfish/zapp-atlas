import type { Body } from "@/schema/bodies";

import { get, send } from "./client";
import type { Experiment } from "./types";

/** An experiment with every exposure event and observation beneath it. */
export const fetchExperiment = (experimentId: number, signal?: AbortSignal) =>
  get<Experiment>(`/experiments/${experimentId}`, signal);

export const createExperiment = (studyId: number, body: Body<"Experiment">) =>
  send<Experiment>("POST", `/studies/${studyId}/experiments`, body);

/** What is sent is what the experiment becomes; its exposure events are left alone. */
export const replaceExperiment = (
  experimentId: number,
  body: Body<"Experiment">,
) => send<Experiment>("PUT", `/experiments/${experimentId}`, body);

export const deleteExperiment = (experimentId: number) =>
  send<null>("DELETE", `/experiments/${experimentId}`);
