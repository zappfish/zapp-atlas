import { get, send } from "./client";
import type { Study, StudyBody, StudySummary } from "./types";

/** A group's studies, drafts included: the caller is one of its members. */
export const fetchGroupStudies = (groupId: number, signal?: AbortSignal) =>
  get<StudySummary[]>(`/studies?research_group=${groupId}`, signal);

export const fetchStudy = (studyId: number, signal?: AbortSignal) =>
  get<Study>(`/studies/${studyId}`, signal);

/**
 * A study with a publication carries `publication`; one without, a nickname.
 *
 * Every new study starts as a draft, which only its research group can see.
 * That `status` is about who may read the study, and is separate from whether
 * it has a publication.
 */
export const createStudy = (
  groupId: number,
  study: { publication?: string; nickname?: string; description?: string },
) => {
  const body: StudyBody = { research_group: groupId, status: "draft", ...study };
  return send<Study>("POST", "/studies", body);
};

export const deleteStudy = (studyId: number) =>
  send<null>("DELETE", `/studies/${studyId}`);
