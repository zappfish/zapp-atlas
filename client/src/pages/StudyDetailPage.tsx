import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { getStudy } from '@/api/studies';
import type {
  ExposureEvent,
  Experiment,
  Phenotype,
  PhenotypeObservationSet,
  Study,
} from '@/types';

function fmtQuantity(q: { numeric_value?: string | null; unit?: string | null } | null | undefined) {
  if (!q) return null;
  return [q.numeric_value, q.unit].filter(Boolean).join(' ');
}

function PhenotypeLine({ p }: { p: Phenotype }) {
  const term = p.phenotype_term_id;
  const label = term?.term_label ?? term?.term_uri ?? '—';
  const prev = fmtQuantity(p.prevalence);
  return (
    <li>
      <strong>{label}</strong>
      {term?.term_uri && <span className="muted"> ({term.term_uri})</span>}
      {p.severity && <span> · severity: {p.severity}</span>}
      {prev && <span> · prevalence: {prev}</span>}
      {p.stage && <span> · stage: {p.stage}</span>}
    </li>
  );
}

function ObservationBlock({ obs }: { obs: PhenotypeObservationSet }) {
  return (
    <div className="obs-block">
      <div className="subhead">Observation #{obs.id}</div>
      {(obs.phenotype ?? []).length === 0 ? (
        <p className="muted">No phenotypes recorded.</p>
      ) : (
        <ul>
          {obs.phenotype!.map((p) => (
            <PhenotypeLine key={p.id} p={p} />
          ))}
        </ul>
      )}
      {(obs.image ?? []).length > 0 && (
        <div className="img-row">
          {obs.image!.map((img) => (
            <img
              key={img.id}
              src={`/images/${img.id}`}
              alt={`observation ${obs.id} image ${img.id}`}
              className="thumb"
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ExposureBlock({ ee }: { ee: ExposureEvent }) {
  return (
    <div className="exposure-block">
      <div className="subhead">Exposure #{ee.id}</div>
      <dl>
        {ee.route && (
          <>
            <dt>Route</dt>
            <dd>{ee.route}</dd>
          </>
        )}
        {ee.exposure_type && (
          <>
            <dt>Type</dt>
            <dd>{ee.exposure_type}</dd>
          </>
        )}
        {(ee.exposure_start_stage || ee.exposure_end_stage) && (
          <>
            <dt>Stages</dt>
            <dd>
              {ee.exposure_start_stage ?? '?'} → {ee.exposure_end_stage ?? '?'}
            </dd>
          </>
        )}
      </dl>
      {(ee.stressor ?? []).length > 0 && (
        <>
          <div className="subhead">Stressors</div>
          <ul>
            {ee.stressor!.map((s) => (
              <li key={s.id}>
                <strong>{s.chemical_id?.chemical_name ?? s.chemical_id?.uri ?? '—'}</strong>
                {s.chemical_id?.chebi_id && (
                  <span className="muted"> ({s.chemical_id.chebi_id})</span>
                )}
                {fmtQuantity(s.concentration) && <span> · {fmtQuantity(s.concentration)}</span>}
                {s.manufacturer && <span> · {s.manufacturer}</span>}
              </li>
            ))}
          </ul>
        </>
      )}
      {(ee.phenotype_observation ?? []).map((obs) => (
        <ObservationBlock key={obs.id} obs={obs} />
      ))}
    </div>
  );
}

function ExperimentBlock({ exp }: { exp: Experiment }) {
  return (
    <div className="experiment-block">
      <h3>
        Experiment #{exp.id}
        {exp.fish?.name && <span className="muted"> — {exp.fish.name}</span>}
      </h3>
      <dl>
        {exp.fish && (
          <>
            <dt>Fish</dt>
            <dd>
              {exp.fish.name} <span className="muted">({exp.fish.zfin_id})</span>
            </dd>
          </>
        )}
        <dt>Standard rearing</dt>
        <dd>{exp.standard_rearing_condition === false ? 'No' : 'Yes'}</dd>
        {exp.rearing_condition_comment && (
          <>
            <dt>Rearing notes</dt>
            <dd>{exp.rearing_condition_comment}</dd>
          </>
        )}
      </dl>
      {(exp.exposure_event ?? []).map((ee) => (
        <ExposureBlock key={ee.id} ee={ee} />
      ))}
    </div>
  );
}

export default function StudyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [study, setStudy] = useState<Study | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setStudy(null);
    setError(null);
    getStudy(id)
      .then((s) => {
        if (!cancelled) setStudy(s);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (error) return <p className="error">Failed to load study: {error}</p>;
  if (!study) return <p>Loading…</p>;

  return (
    <section>
      <p>
        <Link to="/">← All studies</Link>
      </p>
      <h1>{study.publication ?? `Study #${study.id}`}</h1>
      <dl>
        {study.lab && (
          <>
            <dt>Lab</dt>
            <dd>{study.lab}</dd>
          </>
        )}
        {(study.annotator ?? []).length > 0 && (
          <>
            <dt>Annotators</dt>
            <dd>{study.annotator!.join(', ')}</dd>
          </>
        )}
      </dl>
      <h2>Experiments</h2>
      {(study.experiment ?? []).length === 0 ? (
        <p className="muted">No experiments.</p>
      ) : (
        study.experiment!.map((e) => <ExperimentBlock key={e.id} exp={e} />)
      )}
    </section>
  );
}
