import { api } from '@/api';
import type { Experiment, Fish } from '@/types';

export interface ExperimentWritable {
  standard_rearing_condition?: boolean | null;
  rearing_condition_comment?: string | null;
  fish?: Fish | null;
}

export function getExperiment(id: number | string): Promise<Experiment> {
  return api<Experiment>(`/experiments/${id}`);
}

export function createExperimentForStudy(
  studyId: number | string,
  payload: ExperimentWritable,
): Promise<Experiment> {
  return api<Experiment>(`/studies/${studyId}/experiments`, {
    method: 'POST',
    body: { ...payload, control: [], exposure_event: [] },
  });
}

export function patchExperiment(
  id: number | string,
  payload: ExperimentWritable,
): Promise<Experiment> {
  return api<Experiment>(`/experiments/${id}`, { method: 'PATCH', body: payload });
}

export async function deleteExperiment(id: number | string): Promise<void> {
  await api<void>(`/experiments/${id}`, { method: 'DELETE' });
}

export interface ZfinHit {
  id: string;
  name: string;
  value: string;
  url: string;
  category: string;
}

export function fishAutocomplete(q: string): Promise<ZfinHit[]> {
  return api<ZfinHit[]>('/zfin/fish-autocomplete', { query: { q } });
}

export function wildtypeList(q?: string): Promise<{ zfin_id: string; name: string }[]> {
  return api('/zfin/wildtypes', { query: q ? { q } : undefined });
}
