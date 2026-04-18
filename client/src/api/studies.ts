import { api } from '@/api';
import type { Study } from '@/types';

export function listStudies(
  { limit = 50, offset = 0 }: { limit?: number; offset?: number } = {},
): Promise<Study[]> {
  return api<Study[]>('/studies', { query: { limit, offset } });
}

export function getStudy(id: number | string): Promise<Study> {
  return api<Study>(`/studies/${id}`);
}
