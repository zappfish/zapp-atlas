import type { Body } from "@/schema/bodies";

import { get, send } from "./client";
import type { ExposureEvent } from "./types";

export const fetchExposure = (exposureId: number, signal?: AbortSignal) =>
  get<ExposureEvent>(`/exposures/${exposureId}`, signal);

export const createExposure = (
  experimentId: number,
  body: Body<"ExposureEvent">,
) => send<ExposureEvent>("POST", `/experiments/${experimentId}/exposures`, body);

/** What is sent is what the exposure event becomes; its observations are left alone. */
export const replaceExposure = (
  exposureId: number,
  body: Body<"ExposureEvent">,
) => send<ExposureEvent>("PUT", `/exposures/${exposureId}`, body);

export const deleteExposure = (exposureId: number) =>
  send<null>("DELETE", `/exposures/${exposureId}`);
