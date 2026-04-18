import { api } from '@/api';
import type { ChemicalEntity, ExposureEvent, QuantityValue } from '@/types';

export interface StressorWritable {
  chemical_id?: ChemicalEntity | null;
  concentration?: QuantityValue | null;
  manufacturer?: string | null;
}

export interface ExposureWritable {
  route?: string | null;
  exposure_type?: string | null;
  exposure_start_stage?: string | null;
  exposure_end_stage?: string | null;
  comment?: string | null;
  stressor?: StressorWritable[];
}

export function getExposure(id: number | string): Promise<ExposureEvent> {
  return api<ExposureEvent>(`/exposures/${id}`);
}

export function createExposureForExperiment(
  experimentId: number | string,
  payload: ExposureWritable,
): Promise<ExposureEvent> {
  return api<ExposureEvent>(`/experiments/${experimentId}/exposures`, {
    method: 'POST',
    body: { ...payload, phenotype_observation: [] },
  });
}

export function patchExposure(
  id: number | string,
  payload: ExposureWritable,
): Promise<ExposureEvent> {
  return api<ExposureEvent>(`/exposures/${id}`, { method: 'PATCH', body: payload });
}

export interface OntologyHit {
  term_uri: string;
  term_label: string;
}

export function exposureRouteAutocomplete(q: string): Promise<OntologyHit[]> {
  return api<OntologyHit[]>('/ols/exposure-route-autocomplete', { query: { q } });
}

export function exposureTypeAutocomplete(q: string): Promise<OntologyHit[]> {
  return api<OntologyHit[]>('/ols/exposure-type-autocomplete', { query: { q } });
}
