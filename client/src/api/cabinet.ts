/** An entry stores only an identifier; names for display come from ./chemicals. */

import { get, send } from "./client";
import type { CabinetEntry } from "./types";

const root = (groupId: number) =>
  `/research-groups/${groupId}/chemical-cabinet`;

export const fetchCabinet = (groupId: number, signal?: AbortSignal) =>
  get<CabinetEntry[]>(root(groupId), signal);

export const fetchCabinetEntry = (
  groupId: number,
  entryId: number,
  signal?: AbortSignal,
) => get<CabinetEntry>(`${root(groupId)}/${entryId}`, signal);

export const addChemical = (groupId: number, chemicalId: string) =>
  send<CabinetEntry>("POST", root(groupId), { chemical_id: chemicalId });

export const updateChemical = (
  groupId: number,
  entryId: number,
  chemicalId: string,
) =>
  send<CabinetEntry>("PATCH", `${root(groupId)}/${entryId}`, {
    chemical_id: chemicalId,
  });

export const deleteChemical = (groupId: number, entryId: number) =>
  send<null>("DELETE", `${root(groupId)}/${entryId}`);
