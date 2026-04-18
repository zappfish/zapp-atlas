import { api } from '@/api';
import type { Image, PhenotypeObservationSet, PhenotypeTerm } from '@/types';

export interface PhenotypeWritable {
  stage?: string | null;
  severity?: 'mild' | 'moderate' | 'severe' | null;
  phenotype_term_id?: PhenotypeTerm | null;
}

export interface ObservationWritable {
  phenotype?: PhenotypeWritable[];
}

export function getObservation(id: number | string): Promise<PhenotypeObservationSet> {
  return api<PhenotypeObservationSet>(`/observations/${id}`);
}

export function createObservationForExposure(
  exposureId: number | string,
  payload: ObservationWritable,
): Promise<PhenotypeObservationSet> {
  return api<PhenotypeObservationSet>(`/exposures/${exposureId}/observations`, {
    method: 'POST',
    body: { ...payload, image: [], control_image: [] },
  });
}

export function patchObservation(
  id: number | string,
  payload: ObservationWritable,
): Promise<PhenotypeObservationSet> {
  return api<PhenotypeObservationSet>(`/observations/${id}`, {
    method: 'PATCH',
    body: payload,
  });
}

export function uploadObservationImage(
  observationId: number | string,
  file: File,
  metadata: { magnification?: string; resolution?: string; scale_bar?: string } = {},
): Promise<Image> {
  const fd = new FormData();
  fd.append('file', file);
  for (const [k, v] of Object.entries(metadata)) {
    if (v) fd.append(k, v);
  }
  return api<Image>(`/observations/${observationId}/images`, {
    method: 'POST',
    body: fd,
  });
}
