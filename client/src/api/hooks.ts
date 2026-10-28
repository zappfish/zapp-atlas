import {
  queryOptions,
  useMutation,
  useQueries,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  addMember,
  createGroup,
  fetchGroup,
  fetchMembers,
  removeMember,
} from "./groups";
import type { ResearchGroupRole } from "./types";
import { addFish, deleteFish, fetchFishEntry, fetchFishTank } from "./fishTank";
import {
  addChemical,
  deleteChemical,
  fetchCabinet,
  fetchCabinetEntry,
  updateChemical,
} from "./cabinet";
import { normalizeChemical, searchChemicals } from "./chemicals";
import type { Suggestion } from "./chemicals";

/** Query keys, so a mutation can invalidate one section by name. */
export const keys = {
  zpGraph: ["extdata", "zp-graph"] as const,
  chemicalSearch: (q: string) => ["chemicals", "search", q] as const,
  chemical: (id: string) => ["chemicals", id] as const,
  chemicalByCurie: (curie: string) => ["chemicals", "by-curie", curie] as const,
  groups: ["groups"] as const,
  group: (id: number) => ["group", id] as const,
  members: (id: number) => ["group", id, "members"] as const,
  fishTank: (id: number) => ["group", id, "fish-tank"] as const,
  cabinet: (id: number) => ["group", id, "cabinet"] as const,
  fishEntry: (id: number, entryId: number) =>
    ["group", id, "fish-tank", entryId] as const,
  cabinetEntry: (id: number, entryId: number) =>
    ["group", id, "cabinet", entryId] as const,
};

export const MIN_SEARCH_LENGTH = 2;

/**
 * Chemicals matching what has been typed. Held briefly: the same few letters
 * come back as someone edits a name, and the reference data does not move.
 */
export const useChemicalSearch = (q: string) =>
  useQuery({
    queryKey: keys.chemicalSearch(q),
    queryFn: ({ signal }) => searchChemicals(q, signal),
    enabled: q.trim().length >= MIN_SEARCH_LENGTH,
    staleTime: 5 * 60 * 1000,
  });

/**
 * One chemical by an identifier from any source the server accepts; whichever
 * is given, what comes back carries its ChEBI identifier.
 */
export const useChemicalByCurie = (curie: string | null) =>
  useQuery({
    queryKey: keys.chemicalByCurie(curie ?? ""),
    queryFn: async ({ signal }): Promise<Suggestion[]> => {
      const found = await normalizeChemical(curie!, signal);
      return found.primary_id
        ? [{ name: found.label ?? found.primary_id, chebi_ids: [found.primary_id] }]
        : [];
    },
    enabled: curie !== null,
    staleTime: Infinity,
  });

const chemicalQuery = (chebiId: string) =>
  queryOptions({
    queryKey: keys.chemical(chebiId),
    queryFn: ({ signal }) => normalizeChemical(chebiId, signal),
    staleTime: Infinity,
  });

/** The record behind a chosen suggestion. */
export const useChemical = (chebiId: string | null) =>
  useQuery({ ...chemicalQuery(chebiId ?? ""), enabled: chebiId !== null });

/** Each id's name, against the id; the id stands in until its name arrives. */
export const useChemicalNames = (chebiIds: string[]) =>
  useQueries({
    queries: chebiIds.map((id) => chemicalQuery(id)),
    combine: (results) =>
      new Map(chebiIds.map((id, i) => [id, results[i]?.data?.label ?? id])),
  });

/** A group's cabinet on its own, for anything that needs it without the page. */
export const useCabinet = (groupId: number) =>
  useQuery({
    queryKey: keys.cabinet(groupId),
    queryFn: ({ signal }) => fetchCabinet(groupId, signal),
  });

/** One record, for its detail page. */
export const useFishEntry = (groupId: number, entryId: number) =>
  useQuery({
    queryKey: keys.fishEntry(groupId, entryId),
    queryFn: ({ signal }) => fetchFishEntry(groupId, entryId, signal),
  });

export const useCabinetEntry = (groupId: number, entryId: number) =>
  useQuery({
    queryKey: keys.cabinetEntry(groupId, entryId),
    queryFn: ({ signal }) => fetchCabinetEntry(groupId, entryId, signal),
  });

/**
 * Everything one group's dashboard reads. Separate queries so each section can
 * be refetched on its own, issued together since none depends on another.
 */
export const useGroupDashboard = (groupId: number) => {
  const results = useQueries({
    queries: [
      {
        queryKey: keys.group(groupId),
        queryFn: ({ signal }) => fetchGroup(groupId, signal),
      },
      {
        queryKey: keys.members(groupId),
        queryFn: ({ signal }) => fetchMembers(groupId, signal),
      },
      {
        queryKey: keys.fishTank(groupId),
        queryFn: ({ signal }) => fetchFishTank(groupId, signal),
      },
      {
        queryKey: keys.cabinet(groupId),
        queryFn: ({ signal }) => fetchCabinet(groupId, signal),
      },
    ],
  });

  const [group, members, fishTank, cabinet] = results;

  return {
    error: group.error ?? null,
    group: group.data,
    members: members.data ?? [],
    fishTank: {
      rows: fishTank.data ?? [],
      isPending: fishTank.isPending,
      error: fishTank.error ?? null,
    },
    cabinet: {
      rows: cabinet.data ?? [],
      isPending: cabinet.isPending,
      error: cabinet.error ?? null,
    },
  };
};

/**
 * Each mutation refetches only the section it changed, so the rest of the page
 * keeps its data and does not fall back to a skeleton.
 */

export const useCreateGroup = () => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => createGroup(name),
    onSuccess: () => client.invalidateQueries({ queryKey: keys.groups }),
  });
};

/** A group's members on their own, for the dialog that edits them. */
export const useMembers = (groupId: number) =>
  useQuery({
    queryKey: keys.members(groupId),
    queryFn: ({ signal }) => fetchMembers(groupId, signal),
  });

export const useAddMember = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ member, role }: { member: string; role: ResearchGroupRole }) =>
      addMember(groupId, member, role),
    onSuccess: () =>
      client.invalidateQueries({ queryKey: keys.members(groupId) }),
  });
};

export const useRemoveMember = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (memberId: number) => removeMember(groupId, memberId),
    onSuccess: () =>
      client.invalidateQueries({ queryKey: keys.members(groupId) }),
  });
};

export const useAddFish = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (fish: { zfin_id: string; name: string }) =>
      addFish(groupId, fish),
    onSuccess: () =>
      client.invalidateQueries({ queryKey: keys.fishTank(groupId) }),
  });
};

export const useDeleteFish = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (entryId: number) => deleteFish(groupId, entryId),
    onSuccess: (_data, entryId) => {
      client.invalidateQueries({ queryKey: keys.fishTank(groupId) });
      client.removeQueries({ queryKey: keys.fishEntry(groupId, entryId) });
    },
  });
};

/** Refetches a group's cabinet, for a caller that changed several in a row. */
export const useRefreshCabinet = (groupId: number) => {
  const client = useQueryClient();
  return () => client.invalidateQueries({ queryKey: keys.cabinet(groupId) });
};

/** The caller refreshes the cabinet: a dialog adding several does it once. */
export const useAddChemical = (groupId: number) =>
  useMutation({
    mutationFn: ({
      chemicalId,
      nickname,
    }: {
      chemicalId: string;
      nickname?: string;
    }) => addChemical(groupId, chemicalId, nickname),
  });


export const useUpdateChemical = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      entryId,
      ...changes
    }: {
      entryId: number;
      chemicalId?: string;
      nickname?: string | null;
    }) => updateChemical(groupId, entryId, changes),
    onSuccess: (_data, { entryId }) => {
      client.invalidateQueries({ queryKey: keys.cabinet(groupId) });
      client.invalidateQueries({
        queryKey: keys.cabinetEntry(groupId, entryId),
      });
    },
  });
};

export const useDeleteChemical = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (entryId: number) => deleteChemical(groupId, entryId),
    onSuccess: (_data, entryId) => {
      client.invalidateQueries({ queryKey: keys.cabinet(groupId) });
      client.removeQueries({ queryKey: keys.cabinetEntry(groupId, entryId) });
    },
  });
};
