import {
  useMutation,
  useQueries,
  useQueryClient,
} from "@tanstack/react-query";
import {
  addChemical,
  addFish,
  deleteChemical,
  deleteFish,
  fetchCabinet,
  fetchFishTank,
  fetchGroup,
  fetchMembers,
  updateChemical,
} from "./groups";

/** Query keys, so a mutation can invalidate one section by name. */
export const keys = {
  groups: ["groups"] as const,
  group: (id: number) => ["group", id] as const,
  members: (id: number) => ["group", id, "members"] as const,
  fishTank: (id: number) => ["group", id, "fish-tank"] as const,
  cabinet: (id: number) => ["group", id, "cabinet"] as const,
};

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
    fishTank: { rows: fishTank.data ?? [], isPending: fishTank.isPending },
    cabinet: { rows: cabinet.data ?? [], isPending: cabinet.isPending },
  };
};

/**
 * Each mutation refetches only the section it changed, so the rest of the page
 * keeps its data and does not fall back to a skeleton.
 */

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
    onSuccess: () =>
      client.invalidateQueries({ queryKey: keys.fishTank(groupId) }),
  });
};

export const useAddChemical = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (chemicalId: string) => addChemical(groupId, chemicalId),
    onSuccess: () =>
      client.invalidateQueries({ queryKey: keys.cabinet(groupId) }),
  });
};

export const useUpdateChemical = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ entryId, chemicalId }: { entryId: number; chemicalId: string }) =>
      updateChemical(groupId, entryId, chemicalId),
    onSuccess: () =>
      client.invalidateQueries({ queryKey: keys.cabinet(groupId) }),
  });
};

export const useDeleteChemical = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (entryId: number) => deleteChemical(groupId, entryId),
    onSuccess: () =>
      client.invalidateQueries({ queryKey: keys.cabinet(groupId) }),
  });
};
