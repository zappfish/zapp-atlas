/** Studies are not yet listed per group; see the group dashboard. */

import { get, send } from "./client";
import type { Study } from "./types";

export const fetchStudy = (studyId: number, signal?: AbortSignal) =>
  get<Study>(`/studies/${studyId}`, signal);

/** A published study carries `publication`; an unpublished one a nickname. */
export const createStudy = (
  groupId: number,
  study: { publication?: string; nickname?: string; description?: string },
) => send<Study>("POST", "/studies", { research_group: groupId, ...study });

export const deleteStudy = (studyId: number) =>
  send<null>("DELETE", `/studies/${studyId}`);
