import { api } from '@/api';
import type { Study } from '@/types';

export interface StudyWritable {
  publication?: string | null;
  lab?: string | null;
  annotator?: string[] | null;
}

export function listStudies(
  { limit = 50, offset = 0 }: { limit?: number; offset?: number } = {},
): Promise<Study[]> {
  return api<Study[]>('/studies', { query: { limit, offset } });
}

export function getStudy(id: number | string): Promise<Study> {
  return api<Study>(`/studies/${id}`);
}

export function createStudy(payload: StudyWritable): Promise<Study> {
  return api<Study>('/studies', {
    method: 'POST',
    body: { ...payload, experiment: [] },
  });
}

export function patchStudy(id: number | string, payload: StudyWritable): Promise<Study> {
  return api<Study>(`/studies/${id}`, { method: 'PATCH', body: payload });
}
