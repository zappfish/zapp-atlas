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
  fetchGroups,
  fetchMembers,
  removeMember,
} from "./groups";
import type {
  FishDescription,
  FishTankEntryBody,
  ResearchGroupRole,
} from "./types";
import { addFish, deleteFish, fetchFishEntry, fetchFishTank } from "./fishTank";
import { fetchWildtypes, resolveFish, searchAlleles } from "./zfin";
import {
  addChemical,
  deleteChemical,
  fetchCabinet,
  fetchCabinetEntry,
  updateChemical,
} from "./cabinet";
import { normalizeChemical, searchChemicals } from "./chemicals";
import {
  createStudy,
  deleteStudy,
  fetchGroupStudies,
  fetchStudy,
  replaceStudy,
} from "./studies";
import type { StudyBody } from "./types";
import {
  createExperiment,
  deleteExperiment,
  replaceExperiment,
} from "./experiments";
import { createExposure, deleteExposure, replaceExposure } from "./exposures";
import {
  createObservation,
  deleteObservation,
  replaceObservation,
} from "./observations";
import { deleteImage, replaceImage, uploadImage } from "./images";
import type { Body } from "@/schema/bodies";
import type { Suggestion } from "./chemicals";

/** Query keys, so a mutation can invalidate one section by name. */
export const keys = {
  zpGraph: ["extdata", "zp-graph"] as const,
  chemicalSearch: (q: string) => ["chemicals", "search", q] as const,
  chemical: (id: string) => ["chemicals", id] as const,
  chemicalByCurie: (curie: string) => ["chemicals", "by-curie", curie] as const,
  groups: ["groups"] as const,
  study: (id: number) => ["studies", id] as const,
  group: (id: number) => ["group", id] as const,
  members: (id: number) => ["group", id, "members"] as const,
  fishTank: (id: number) => ["group", id, "fish-tank"] as const,
  cabinet: (id: number) => ["group", id, "cabinet"] as const,
  groupStudies: (id: number) => ["group", id, "studies"] as const,
  fishEntry: (id: number, entryId: number) =>
    ["group", id, "fish-tank", entryId] as const,
  cabinetEntry: (id: number, entryId: number) =>
    ["group", id, "cabinet", entryId] as const,
  wildtypes: ["zfin", "wildtypes"] as const,
  alleleSearch: (q: string) => ["zfin", "alleles", q] as const,
  resolveFish: (description: FishDescription) =>
    ["zfin", "resolve", description] as const,
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

/** A group on its own, for pages that need only its name. */
export const useGroup = (groupId: number) =>
  useQuery({
    queryKey: keys.group(groupId),
    queryFn: ({ signal }) => fetchGroup(groupId, signal),
  });

/** A group's tank on its own, for the form's fish panel. */
export const useFishTank = (groupId: number) =>
  useQuery({
    queryKey: keys.fishTank(groupId),
    queryFn: ({ signal }) => fetchFishTank(groupId, signal),
  });

/** A group's cabinet on its own, for anything that needs it without the page. */
export const useCabinet = (groupId: number) =>
  useQuery({
    queryKey: keys.cabinet(groupId),
    queryFn: ({ signal }) => fetchCabinet(groupId, signal),
  });

/** ZFIN's wild-type lines. Reference data from the bundle: it does not move. */
export const useWildtypes = () =>
  useQuery({
    queryKey: keys.wildtypes,
    queryFn: ({ signal }) => fetchWildtypes(signal),
    staleTime: Infinity,
  });

/** ZFIN alleles matching what has been typed, by symbol, gene or construct. */
export const useAlleleSearch = (q: string) =>
  useQuery({
    queryKey: keys.alleleSearch(q),
    queryFn: ({ signal }) => searchAlleles(q, signal),
    enabled: q.trim().length >= MIN_SEARCH_LENGTH,
    staleTime: Infinity,
  });

/**
 * What ZFIN has registered for a description, or nothing when there is no
 * description yet. Cached for good: the bundle does not change while the app
 * runs.
 */
export const useResolveFish = (description: FishDescription | null) => {
  const asked = description ?? NO_DESCRIPTION;
  return useQuery({
    queryKey: keys.resolveFish(asked),
    queryFn: ({ signal }) => resolveFish(asked, signal),
    enabled: description !== null,
    staleTime: Infinity,
  });
};

/** Stands in for a missing description so the query has a stable key; never sent. */
const NO_DESCRIPTION: FishDescription = { alleles: [], reagents: [] };

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
      retry: () => void fishTank.refetch(),
    },
    cabinet: {
      rows: cabinet.data ?? [],
      isPending: cabinet.isPending,
      error: cabinet.error ?? null,
      retry: () => void cabinet.refetch(),
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
    mutationFn: (entry: FishTankEntryBody) => addFish(groupId, entry),
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

/** A group's studies, for its page. */
export const useGroupStudies = (groupId: number) =>
  useQuery({
    queryKey: keys.groupStudies(groupId),
    queryFn: ({ signal }) => fetchGroupStudies(groupId, signal),
  });

/**
 * The studies of every group the caller belongs to, each with its group.
 * Asked for a group at a time, so a group's page and this share what is held.
 */
export const useMyStudies = () => {
  const groups = useQuery({
    queryKey: keys.groups,
    queryFn: ({ signal }) => fetchGroups(signal),
  });
  return useQueries({
    queries: (groups.data ?? []).map((group) => ({
      queryKey: keys.groupStudies(group.id),
      queryFn: ({ signal }: { signal: AbortSignal }) =>
        fetchGroupStudies(group.id, signal),
    })),
    combine: (results) => ({
      isPending: groups.isPending || results.some((each) => each.isPending),
      studies: results.flatMap((each, i) =>
        (each.data ?? []).map((study) => ({ study, group: groups.data![i]! })),
      ),
    }),
  });
};

/** One study, for its page. */
export const useStudy = (studyId: number) =>
  useQuery({
    queryKey: keys.study(studyId),
    queryFn: ({ signal }) => fetchStudy(studyId, signal),
  });

/** Seeds the new study's cache entry, so its page opens without a refetch. */
export const useCreateStudy = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (study: Parameters<typeof createStudy>[1]) =>
      createStudy(groupId, study),
    onSuccess: (study) => {
      if (study) client.setQueryData(keys.study(study.id), study);
      client.invalidateQueries({ queryKey: keys.groupStudies(groupId) });
    },
  });
};

/** The answer is the study as it now stands, so its page needs no refetch. */
export const useReplaceStudy = (groupId: number, studyId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (body: StudyBody) => replaceStudy(studyId, body),
    onSuccess: (study) => {
      if (study) client.setQueryData(keys.study(studyId), study);
      client.invalidateQueries({ queryKey: keys.groupStudies(groupId) });
    },
  });
};

export const useDeleteStudy = (groupId: number) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (studyId: number) => deleteStudy(studyId),
    onSuccess: (_data, studyId) => {
      client.removeQueries({ queryKey: keys.study(studyId) });
      client.invalidateQueries({ queryKey: keys.groupStudies(groupId) });
    },
  });
};

/**
 * Saving beneath a study. Its page and its experiments' pages all read the
 * one study, which the API returns whole, so every save refreshes that.
 */
const useStudyMutation = <Sent, Answer>(
  studyId: number,
  mutationFn: (sent: Sent) => Promise<Answer>,
) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => client.invalidateQueries({ queryKey: keys.study(studyId) }),
  });
};

/** Creates the experiment when it has no id yet, and replaces it otherwise. */
export const useSaveExperiment = (studyId: number, experimentId: number | null) =>
  useStudyMutation(studyId, (body: Body<"Experiment">) =>
    experimentId === null
      ? createExperiment(studyId, body)
      : replaceExperiment(experimentId, body),
  );

export const useDeleteExperiment = (studyId: number) =>
  useStudyMutation(studyId, deleteExperiment);

/** Creates the exposure event when it has no id yet, and replaces it otherwise. */
export const useSaveExposure = (
  studyId: number,
  experimentId: number,
  exposureId: number | null,
) =>
  useStudyMutation(studyId, (body: Body<"ExposureEvent">) =>
    exposureId === null
      ? createExposure(experimentId, body)
      : replaceExposure(exposureId, body),
  );

export const useDeleteExposure = (studyId: number) =>
  useStudyMutation(studyId, deleteExposure);

/** Creates the observation when it has no id yet, and replaces it otherwise. */
export const useSaveObservation = (
  studyId: number,
  exposureId: number,
  observationId: number | null,
) =>
  useStudyMutation(studyId, (body: Body<"PhenotypeObservationSet">) =>
    observationId === null
      ? createObservation(exposureId, body)
      : replaceObservation(observationId, body),
  );

export const useDeleteObservation = (studyId: number) =>
  useStudyMutation(studyId, deleteObservation);

/** A new image: its file, uploaded once, with what is said about it. */
export const useUploadImage = (studyId: number, observationId: number) =>
  useStudyMutation(
    studyId,
    ({ file, description }: { file: File; description: Body<"Image"> }) =>
      uploadImage(observationId, file, description),
  );

/** What is said about an image. Its file stays as uploaded. */
export const useReplaceImage = (studyId: number, imageId: number) =>
  useStudyMutation(studyId, (description: Body<"Image">) =>
    replaceImage(imageId, description),
  );

export const useDeleteImage = (studyId: number) =>
  useStudyMutation(studyId, deleteImage);
