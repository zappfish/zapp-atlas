import { useQueries } from "@tanstack/react-query";
import {
  fetchCabinet,
  fetchFishTank,
  fetchGroup,
  fetchMembers,
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
