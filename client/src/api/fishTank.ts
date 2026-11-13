import { get, send } from "./client";
import type { FishTankEntry } from "./types";

const root = (groupId: number) => `/research-groups/${groupId}/fish-tank`;

export const fetchFishTank = (groupId: number, signal?: AbortSignal) =>
  get<FishTankEntry[]>(root(groupId), signal);

export const fetchFishEntry = (
  groupId: number,
  entryId: number,
  signal?: AbortSignal,
) => get<FishTankEntry>(`${root(groupId)}/${entryId}`, signal);

export const addFish = (
  groupId: number,
  fish: { zfin_id: string; name: string },
) => send<FishTankEntry>("POST", root(groupId), { fish });

export const deleteFish = (groupId: number, entryId: number) =>
  send<null>("DELETE", `${root(groupId)}/${entryId}`);
