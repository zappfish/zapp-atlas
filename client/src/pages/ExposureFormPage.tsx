import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import {
  createExposureForExperiment,
  exposureRouteAutocomplete,
  exposureTypeAutocomplete,
  getExposure,
  patchExposure,
  type ExposureWritable,
  type OntologyHit,
  type StressorWritable,
} from '@/api/exposures';
import OntologyAutocomplete from '@/components/OntologyAutocomplete';
import type { ChemicalEntity, StressorChemical } from '@/types';

function toHit(uri: string | null | undefined, label: string | null | undefined): OntologyHit | null {
  if (!uri) return null;
  return { term_uri: uri, term_label: label ?? '' };
}

function blankStressor(): StressorWritable {
  return {
    chemical_id: {
      uri: '',
      chebi_id: '',
      cas_id: '',
      chemical_name: '',
    },
    concentration: { numeric_value: '', unit: '' },
    manufacturer: '',
  };
}

function fromStressor(s: StressorChemical): StressorWritable {
  return {
    chemical_id: s.chemical_id ?? blankStressor().chemical_id,
    concentration: s.concentration ?? { numeric_value: '', unit: '' },
    manufacturer: s.manufacturer ?? '',
  };
}

export default function ExposureFormPage() {
  const { experimentId, id } = useParams<{ experimentId: string; id: string }>();
  const nav = useNavigate();
  const isEdit = !!id;

  const [route, setRoute] = useState<OntologyHit | null>(null);
  const [exposureType, setExposureType] = useState<OntologyHit | null>(null);
  const [startStage, setStartStage] = useState('');
  const [endStage, setEndStage] = useState('');
  const [comment, setComment] = useState('');
  const [stressor, setStressor] = useState<StressorWritable>(blankStressor());
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isEdit) return;
    let cancelled = false;
    getExposure(id!)
      .then((ee) => {
        if (cancelled) return;
        setRoute(toHit(ee.route, null));
        setExposureType(toHit(ee.exposure_type, null));
        setStartStage(ee.exposure_start_stage ?? '');
        setEndStage(ee.exposure_end_stage ?? '');
        setComment(ee.comment ?? '');
        if (ee.stressor && ee.stressor.length > 0) {
          setStressor(fromStressor(ee.stressor[0]!));
        }
        setLoading(false);
      })
      .catch((err: Error) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [id, isEdit]);

  function updateChemical<K extends keyof ChemicalEntity>(key: K, value: string) {
    setStressor((s) => ({
      ...s,
      chemical_id: { ...(s.chemical_id ?? {}), [key]: value },
    }));
  }

  function stressorHasContent(): boolean {
    const c = stressor.chemical_id;
    return !!(
      c &&
      (c.chemical_name || c.chebi_id || c.cas_id || c.uri)
    );
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const payload: ExposureWritable = {
      route: route?.term_uri ?? null,
      exposure_type: exposureType?.term_uri ?? null,
      exposure_start_stage: startStage || null,
      exposure_end_stage: endStage || null,
      comment: comment || null,
      stressor: stressorHasContent() ? [stressor] : [],
    };

    try {
      if (isEdit) {
        await patchExposure(id!, payload);
        nav(-1);
      } else {
        await createExposureForExperiment(experimentId!, payload);
        nav(-1);
      }
    } catch (err) {
      setError((err as Error).message);
      setSaving(false);
    }
  }

  if (loading) return <p>Loading…</p>;

  return (
    <section>
      <h1>{isEdit ? 'Edit exposure' : 'New exposure'}</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit} className="stacked-form">
        <label>
          Route
          <OntologyAutocomplete
            value={route}
            onChange={setRoute}
            search={exposureRouteAutocomplete}
            placeholder="Start typing a route (e.g. inhalation)…"
            ariaLabel="Route autocomplete"
          />
        </label>
        <label>
          Exposure type
          <OntologyAutocomplete
            value={exposureType}
            onChange={setExposureType}
            search={exposureTypeAutocomplete}
            placeholder="Start typing an ECTO term…"
            ariaLabel="Exposure type autocomplete"
          />
        </label>
        <div className="field-row">
          <label>
            Start stage
            <input
              value={startStage}
              onChange={(e) => setStartStage(e.target.value)}
              placeholder="ZFS:0000011"
            />
          </label>
          <label>
            End stage
            <input
              value={endStage}
              onChange={(e) => setEndStage(e.target.value)}
              placeholder="ZFS:0000039"
            />
          </label>
        </div>

        <fieldset className="sub-form">
          <legend>Stressor (optional)</legend>
          <label>
            Chemical name
            <input
              value={stressor.chemical_id?.chemical_name ?? ''}
              onChange={(e) => updateChemical('chemical_name', e.target.value)}
            />
          </label>
          <div className="field-row">
            <label>
              ChEBI ID
              <input
                value={stressor.chemical_id?.chebi_id ?? ''}
                onChange={(e) => updateChemical('chebi_id', e.target.value)}
                placeholder="CHEBI:33216"
              />
            </label>
            <label>
              CAS ID
              <input
                value={stressor.chemical_id?.cas_id ?? ''}
                onChange={(e) => updateChemical('cas_id', e.target.value)}
                placeholder="80-05-7"
              />
            </label>
          </div>
          <label>
            URI
            <input
              value={stressor.chemical_id?.uri ?? ''}
              onChange={(e) => updateChemical('uri', e.target.value)}
              placeholder="http://purl.obolibrary.org/obo/CHEBI_33216"
            />
          </label>
          <div className="field-row">
            <label>
              Concentration
              <input
                value={stressor.concentration?.numeric_value ?? ''}
                onChange={(e) =>
                  setStressor((s) => ({
                    ...s,
                    concentration: { ...(s.concentration ?? {}), numeric_value: e.target.value },
                  }))
                }
              />
            </label>
            <label>
              Unit
              <input
                value={stressor.concentration?.unit ?? ''}
                onChange={(e) =>
                  setStressor((s) => ({
                    ...s,
                    concentration: { ...(s.concentration ?? {}), unit: e.target.value },
                  }))
                }
                placeholder="µg/L"
              />
            </label>
          </div>
          <label>
            Manufacturer
            <input
              value={stressor.manufacturer ?? ''}
              onChange={(e) => setStressor((s) => ({ ...s, manufacturer: e.target.value }))}
            />
          </label>
        </fieldset>

        <label>
          Comment
          <textarea
            rows={2}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </label>

        <div className="form-actions">
          <button type="submit" disabled={saving}>
            {saving ? 'Saving…' : isEdit ? 'Save' : 'Create exposure'}
          </button>
          <button type="button" onClick={() => nav(-1)} disabled={saving}>
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}
