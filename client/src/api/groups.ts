import { get, send } from "./client";
import type { Group, Member } from "./types";

export const fetchGroups = (signal?: AbortSignal) =>
  get<Group[]>("/research-groups", signal);

export const fetchGroup = (groupId: number, signal?: AbortSignal) =>
  get<Group>(`/research-groups/${groupId}`, signal);

export const fetchMembers = (groupId: number, signal?: AbortSignal) =>
  get<Member[]>(`/research-groups/${groupId}/members`, signal);

/** The caller becomes its first admin. */
export const createGroup = (name: string) =>
  send<Group>("POST", "/research-groups", { name });
