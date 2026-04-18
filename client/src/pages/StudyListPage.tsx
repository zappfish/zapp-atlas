import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { listStudies } from '@/api/studies';
import type { Study } from '@/types';

export default function StudyListPage() {
  const [studies, setStudies] = useState<Study[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listStudies()
      .then((rows) => {
        if (!cancelled) setStudies(rows);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) return <p className="error">Failed to load studies: {error}</p>;
  if (studies === null) return <p>Loading studies…</p>;

  return (
    <section>
      <div className="page-head">
        <h1>Studies</h1>
        <Link to="/studies/new" className="button-link">
          New study
        </Link>
      </div>
      {studies.length === 0 ? (
        <p>No studies yet.</p>
      ) : (
        <table className="study-table">
          <thead>
            <tr>
              <th>Publication</th>
              <th>Lab</th>
              <th>Annotators</th>
              <th>Experiments</th>
            </tr>
          </thead>
          <tbody>
            {studies.map((s) => (
              <tr key={s.id}>
                <td>
                  <Link to={`/studies/${s.id}`}>{s.publication ?? '—'}</Link>
                </td>
                <td>{s.lab ?? '—'}</td>
                <td>{(s.annotator ?? []).join(', ') || '—'}</td>
                <td>{(s.experiment ?? []).length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
