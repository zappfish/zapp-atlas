import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { imageUrl } from '@/api';
import {
  createObservationForExposure,
  getObservation,
  patchObservation,
  uploadObservationImage,
  type PhenotypeWritable,
} from '@/api/observations';
import PhenotypeModal from '@/components/PhenotypeModal';
import type { Phenotype, PhenotypeObservationSet, PhenotypeTerm } from '@/types';

const SEVERITIES = ['mild', 'moderate', 'severe'] as const;
type Severity = (typeof SEVERITIES)[number];

interface PhenotypeDraft {
  stage: string;
  severity: Severity | '';
  prevalence: string;
  prevalenceUnit: string;
  term: PhenotypeTerm | null;
}

function blankPhenotype(): PhenotypeDraft {
  return { stage: '', severity: '', prevalence: '', prevalenceUnit: '%', term: null };
}

function fromPhenotype(p: Phenotype): PhenotypeDraft {
  return {
    stage: p.stage ?? '',
    severity: (p.severity as Severity) ?? '',
    prevalence: p.prevalence?.numeric_value ?? '',
    prevalenceUnit: p.prevalence?.unit ?? '%',
    term: p.phenotype_term_id ?? null,
  };
}

function toWritable(draft: PhenotypeDraft): PhenotypeWritable {
  const prevalence = draft.prevalence
    ? { numeric_value: draft.prevalence, unit: draft.prevalenceUnit || null }
    : null;
  return {
    stage: draft.stage || null,
    severity: draft.severity || null,
    phenotype_term_id: draft.term,
    ...(prevalence ? { prevalence } : {}),
  } as PhenotypeWritable;
}

function hasContent(draft: PhenotypeDraft): boolean {
  return !!(draft.term || draft.stage || draft.severity || draft.prevalence);
}

export default function ObservationFormPage() {
  const { exposureId, id } = useParams<{ exposureId: string; id: string }>();
  const nav = useNavigate();
  const isEdit = !!id;

  const [phenotypes, setPhenotypes] = useState<PhenotypeDraft[]>([blankPhenotype()]);
  const [pickerFor, setPickerFor] = useState<number | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [existingObs, setExistingObs] = useState<PhenotypeObservationSet | null>(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isEdit) return;
    let cancelled = false;
    getObservation(id!)
      .then((obs) => {
        if (cancelled) return;
        setExistingObs(obs);
        if (obs.phenotype && obs.phenotype.length > 0) {
          setPhenotypes(obs.phenotype.map(fromPhenotype));
        }
        setLoading(false);
      })
      .catch((err: Error) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [id, isEdit]);

  function patchRow(i: number, next: Partial<PhenotypeDraft>) {
    setPhenotypes((rows) => rows.map((r, idx) => (idx === i ? { ...r, ...next } : r)));
  }
  function addRow() {
    setPhenotypes((rows) => [...rows, blankPhenotype()]);
  }
  function removeRow(i: number) {
    setPhenotypes((rows) => (rows.length === 1 ? [blankPhenotype()] : rows.filter((_, idx) => idx !== i)));
  }

  function addFiles(incoming: FileList | File[] | null) {
    if (!incoming) return;
    const list = Array.from(incoming).filter((f) => f.type.startsWith('image/'));
    setFiles((prev) => [...prev, ...list]);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const phenotype = phenotypes.filter(hasContent).map(toWritable);

    try {
      let obsId: number;
      if (isEdit) {
        const saved = await patchObservation(id!, { phenotype });
        obsId = saved.id;
      } else {
        const saved = await createObservationForExposure(exposureId!, { phenotype });
        obsId = saved.id;
      }

      for (const f of files) {
        await uploadObservationImage(obsId, f);
      }

      nav(-1);
    } catch (err) {
      setError((err as Error).message);
      setSaving(false);
    }
  }

  if (loading) return <p>Loading…</p>;

  return (
    <section>
      <h1>{isEdit ? 'Edit observation' : 'New observation'}</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit} className="stacked-form">
        {phenotypes.map((row, i) => (
          <fieldset className="sub-form" key={i}>
            <legend>
              Phenotype {i + 1}
              <button
                type="button"
                className="link-button sub-form-remove"
                onClick={() => removeRow(i)}
                aria-label={`Remove phenotype ${i + 1}`}
              >
                remove
              </button>
            </legend>

            <div className="field">
              <label>Phenotype term</label>
              {row.term ? (
                <div className="selected-fish">
                  <strong>{row.term.term_label || '—'}</strong>
                  <span className="muted"> ({row.term.term_uri})</span>
                  <button
                    type="button"
                    className="link-button"
                    onClick={() => patchRow(i, { term: null })}
                  >
                    change
                  </button>
                </div>
              ) : (
                <div className="phenotype-entry">
                  <button type="button" onClick={() => setPickerFor(i)}>
                    Pick a phenotype
                  </button>
                  <span className="muted">or paste a CURIE:</span>
                  <input
                    aria-label={`Phenotype CURIE ${i + 1}`}
                    placeholder="ZP:0105827"
                    onKeyDown={(e) => {
                      if (e.key !== 'Enter') return;
                      e.preventDefault();
                      const curie = (e.currentTarget.value || '').trim();
                      if (!curie) return;
                      // PhenotypeTerm has term_label as part of its composite
                      // primary key on the server, so we can't send null.
                      // Seed with the CURIE as a placeholder label; curators
                      // can replace via the picker when OLS/frogpot is up.
                      patchRow(i, { term: { term_uri: curie, term_label: curie } });
                      e.currentTarget.value = '';
                    }}
                  />
                </div>
              )}
            </div>

            <label>
              Observation stage
              <input
                value={row.stage}
                onChange={(e) => patchRow(i, { stage: e.target.value })}
                placeholder="ZFS:0000035"
                aria-label={`Observation stage ${i + 1}`}
              />
            </label>

            <div className="field-row">
              <label>
                Severity
                <select
                  value={row.severity}
                  onChange={(e) => patchRow(i, { severity: e.target.value as Severity | '' })}
                >
                  <option value="">—</option>
                  {SEVERITIES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Prevalence
                <input
                  value={row.prevalence}
                  onChange={(e) => patchRow(i, { prevalence: e.target.value })}
                  placeholder="60"
                />
              </label>
              <label>
                Unit
                <input
                  value={row.prevalenceUnit}
                  onChange={(e) => patchRow(i, { prevalenceUnit: e.target.value })}
                />
              </label>
            </div>
          </fieldset>
        ))}
        <button type="button" onClick={addRow} className="button-link small self-start">
          + Add phenotype
        </button>

        <div className="field">
          <label>Images</label>
          {existingObs?.image && existingObs.image.length > 0 && (
            <div className="img-row">
              {existingObs.image.map((img) => (
                <img
                  key={img.id}
                  src={imageUrl(img.id)}
                  alt={`image ${img.id}`}
                  className="thumb"
                />
              ))}
            </div>
          )}
          <div
            className={`drop-zone${dragging ? ' drag-over' : ''}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              addFiles(e.dataTransfer.files);
            }}
          >
            <p className="muted">Drag image files here, or pick via the button.</p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => addFiles(e.target.files)}
              aria-label="Image files"
            />
            {files.length > 0 && (
              <ul>
                {files.map((f, i) => (
                  <li key={i}>
                    {f.name} <span className="muted">({Math.round(f.size / 1024)} KB)</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={saving}>
            {saving ? 'Saving…' : isEdit ? 'Save' : 'Create observation'}
          </button>
          <button type="button" onClick={() => nav(-1)} disabled={saving}>
            Cancel
          </button>
        </div>
      </form>
      <PhenotypeModal
        open={pickerFor !== null}
        onClose={() => setPickerFor(null)}
        onSelect={(t) => {
          if (pickerFor !== null) patchRow(pickerFor, { term: t });
        }}
      />
    </section>
  );
}
