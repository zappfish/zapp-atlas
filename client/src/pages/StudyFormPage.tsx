import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { createStudy, getStudy, patchStudy } from '@/api/studies';

export default function StudyFormPage() {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const isEdit = !!id;

  const [publication, setPublication] = useState('');
  const [lab, setLab] = useState('');
  const [annotators, setAnnotators] = useState(''); // comma-separated ORCIDs
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isEdit) return;
    let cancelled = false;
    getStudy(id!)
      .then((s) => {
        if (cancelled) return;
        setPublication(s.publication ?? '');
        setLab(s.lab ?? '');
        setAnnotators((s.annotator ?? []).join(', '));
        setLoading(false);
      })
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [id, isEdit]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    const payload = {
      publication: publication || null,
      lab: lab || null,
      annotator: annotators
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    };
    try {
      const saved = isEdit ? await patchStudy(id!, payload) : await createStudy(payload);
      nav(`/studies/${saved.id}`);
    } catch (err) {
      setError((err as Error).message);
      setSaving(false);
    }
  }

  if (loading) return <p>Loading…</p>;

  return (
    <section>
      <h1>{isEdit ? 'Edit study' : 'New study'}</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit} className="stacked-form">
        <label>
          Publication
          <input
            value={publication}
            onChange={(e) => setPublication(e.target.value)}
            placeholder="PMID:22194820 or DOI:…"
          />
        </label>
        <label>
          Lab
          <input
            value={lab}
            onChange={(e) => setLab(e.target.value)}
            placeholder="ZFIN:ZDB-LAB-…"
          />
        </label>
        <label>
          Annotators
          <input
            value={annotators}
            onChange={(e) => setAnnotators(e.target.value)}
            placeholder="ORCID:0000-…, ORCID:0000-…"
          />
          <small className="muted">Comma-separated ORCID identifiers.</small>
        </label>
        <div className="form-actions">
          <button type="submit" disabled={saving}>
            {saving ? 'Saving…' : isEdit ? 'Save' : 'Create study'}
          </button>
          <button
            type="button"
            onClick={() => nav(isEdit ? `/studies/${id}` : '/')}
            disabled={saving}
          >
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}
