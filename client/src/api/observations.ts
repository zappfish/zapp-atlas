import type { Body } from "@/schema/bodies";

import { get, send } from "./client";
import type { Observation } from "./types";

export const fetchObservation = (observationId: number, signal?: AbortSignal) =>
  get<Observation>(`/observations/${observationId}`, signal);

export const createObservation = (
  exposureId: number,
  body: Body<"PhenotypeObservationSet">,
) => send<Observation>("POST", `/exposures/${exposureId}/observations`, body);

/** What is sent is what the observation becomes; its images are left alone. */
export const replaceObservation = (
  observationId: number,
  body: Body<"PhenotypeObservationSet">,
) => send<Observation>("PUT", `/observations/${observationId}`, body);

export const deleteObservation = (observationId: number) =>
  send<null>("DELETE", `/observations/${observationId}`);
