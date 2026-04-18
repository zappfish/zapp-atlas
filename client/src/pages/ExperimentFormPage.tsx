import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import {
  createExperimentForStudy,
  getExperiment,
  patchExperiment,
} from '@/api/experiments';
import FishAutocomplete from '@/components/FishAutocomplete';
import type { Experiment, Fish } from '@/types';

export default function ExperimentFormPage() {
  const { studyId, id } = useParams<{ studyId: string; id: string }>();
  const nav = useNavigate();
  const isEdit = !!id;

  const [fish, setFish] = useState<Fish | null>(null);
  const [standardRearing, setStandardRearing] = useState(true);
  const [rearingComment, setRearingComment] = useState('');
  const [parentStudyId, setParentStudyId] = useState<number | null>(null);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isEdit) return;
    let cancelled = false;
    getExperiment(id!)
      .then(async (e: Experiment) => {
        if (cancelled) return;
        setFish(e.fish ?? null);
        setStandardRearing(e.standard_rearing_condition !== false);
        setRearingComment(e.rearing_condition_comment ?? '');
        // Experiment has no back-pointer to study in the read model, so
        // we rely on the URL when saving; for the cancel-link we fetch
        // through the list if needed.
        setLoading(false);
      })
      .catch((err: Error) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [id, isEdit]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!fish) {
      setError('Pick a fish from ZFIN before saving.');
      return;
    }
    setSaving(true);
    setError(null);
    const payload = {
      fish,
      standard_rearing_condition: standardRearing,
      rearing_condition_comment: standardRearing ? '' : rearingComment,
    };
    try {
      if (isEdit) {
        await patchExperiment(id!, payload);
        nav(-1);
      } else {
        await createExperimentForStudy(studyId!, payload);
        nav(`/studies/${studyId}`);
      }
    } catch (err) {
      setError((err as Error).message);
      setSaving(false);
    }
  }

  if (loading) return <p>Loading…</p>;

  return (
    <section>
      <h1>{isEdit ? 'Edit experiment' : 'New experiment'}</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit} className="stacked-form">
        <label>
          Fish
          <FishAutocomplete value={fish} onChange={setFish} />
        </label>

        <label className="inline-check">
          <input
            type="checkbox"
            checked={standardRearing}
            onChange={(e) => setStandardRearing(e.target.checked)}
          />
          Standard rearing conditions
        </label>

        {!standardRearing && (
          <label>
            Rearing notes
            <textarea
              value={rearingComment}
              onChange={(e) => setRearingComment(e.target.value)}
              rows={3}
              placeholder="What deviated from standard?"
            />
          </label>
        )}

        <div className="form-actions">
          <button type="submit" disabled={saving}>
            {saving ? 'Saving…' : isEdit ? 'Save' : 'Create experiment'}
          </button>
          <button type="button" onClick={() => nav(-1)} disabled={saving}>
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}
