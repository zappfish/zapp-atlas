import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import {
  createObservationForExposure,
  getObservation,
  patchObservation,
  uploadObservationImage,
  type PhenotypeWritable,
} from '@/api/observations';
import PhenotypeModal from '@/components/PhenotypeModal';
import type { PhenotypeObservationSet, PhenotypeTerm } from '@/types';

const SEVERITIES = ['mild', 'moderate', 'severe'] as const;
type Severity = (typeof SEVERITIES)[number];

export default function ObservationFormPage() {
  const { exposureId, id } = useParams<{ exposureId: string; id: string }>();
  const nav = useNavigate();
  const isEdit = !!id;

  const [stage, setStage] = useState('');
  const [severity, setSeverity] = useState<Severity | ''>('');
  const [prevalence, setPrevalence] = useState('');
  const [prevalenceUnit, setPrevalenceUnit] = useState('%');
  const [phenotypeTerm, setPhenotypeTerm] = useState<PhenotypeTerm | null>(null);
  const [pickerOpen, setPickerOpen] = useState(false);
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
        const first = obs.phenotype?.[0];
        if (first) {
          setStage(first.stage ?? '');
          setSeverity((first.severity as Severity) ?? '');
          setPrevalence(first.prevalence?.numeric_value ?? '');
          setPrevalenceUnit(first.prevalence?.unit ?? '%');
          setPhenotypeTerm(first.phenotype_term_id ?? null);
        }
        setLoading(false);
      })
      .catch((err: Error) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [id, isEdit]);

  function addFiles(incoming: FileList | File[] | null) {
    if (!incoming) return;
    const list = Array.from(incoming).filter((f) => f.type.startsWith('image/'));
    setFiles((prev) => [...prev, ...list]);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const pheno: PhenotypeWritable = {
      stage: stage || null,
      severity: severity || null,
      phenotype_term_id: phenotypeTerm,
    };
    const prev = prevalence
      ? { numeric_value: prevalence, unit: prevalenceUnit || null }
      : null;
    const phenoWithPrev = { ...pheno, prevalence: prev };

    try {
      let obsId: number;
      if (isEdit) {
        const payload = { phenotype: phenotypeTerm ? [phenoWithPrev] : [] };
        const saved = await patchObservation(id!, payload);
        obsId = saved.id;
      } else {
        const saved = await createObservationForExposure(exposureId!, {
          phenotype: phenotypeTerm ? [phenoWithPrev] : [],
        });
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
        <label>
          Observation stage
          <input
            value={stage}
            onChange={(e) => setStage(e.target.value)}
            placeholder="ZFS:0000035"
          />
        </label>

        <div className="field-row">
          <label>
            Severity
            <select value={severity} onChange={(e) => setSeverity(e.target.value as Severity | '')}>
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
              value={prevalence}
              onChange={(e) => setPrevalence(e.target.value)}
              placeholder="60"
            />
          </label>
          <label>
            Unit
            <input
              value={prevalenceUnit}
              onChange={(e) => setPrevalenceUnit(e.target.value)}
            />
          </label>
        </div>

        <div className="field">
          <label htmlFor="phenotype-picker">Phenotype term</label>
          {phenotypeTerm ? (
            <div className="selected-fish">
              <strong>{phenotypeTerm.term_label || '—'}</strong>
              <span className="muted"> ({phenotypeTerm.term_uri})</span>
              <button type="button" className="link-button" onClick={() => setPhenotypeTerm(null)}>
                change
              </button>
            </div>
          ) : (
            <button
              type="button"
              id="phenotype-picker"
              onClick={() => setPickerOpen(true)}
            >
              Pick a phenotype
            </button>
          )}
        </div>

        <div className="field">
          <label>Images</label>
          {existingObs?.image && existingObs.image.length > 0 && (
            <div className="img-row">
              {existingObs.image.map((img) => (
                <img
                  key={img.id}
                  src={`/images/${img.id}`}
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
        open={pickerOpen}
        onClose={() => setPickerOpen(false)}
        onSelect={(t) => setPhenotypeTerm(t)}
      />
    </section>
  );
}
