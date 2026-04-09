import React, { useState } from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import { EXPOSURE_SUBSTANCE } from './explanations';
import { SUBSTANCE_IDTYPE_OPTIONS } from './constants';
import { SubstanceIdType } from '@/schema';

type Substance = {
  name?: string;
  idType: SubstanceIdType;
  id?: string;
};

type EqIdentifier = {
  identifier: string | null;
  label: string | null;
  description: string | null;
};

type NormResult = {
  normalized: boolean;
  primary_id: string | null;
  label: string | null;
  description: string | null;
  equivalent_identifiers: EqIdentifier[];
};

type NormState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'done'; result: NormResult; imageB64: string | null };

export default function SubstanceFields({
  value,
  onChange
}: {
  value: Substance;
  onChange: (next: Substance) => void;
}) {
  const [norm, setNorm] = useState<NormState>({ status: 'idle' });

  const applyChange = (partial: Partial<Substance>) => {
    onChange({ ...value, ...partial });
    if ('id' in partial || 'idType' in partial) {
      setNorm({ status: 'idle' });
    }
  };

  const idTypeValue: SubstanceIdType = value.idType ?? 'None';
  const useNameResolver = idTypeValue === 'None';
  const canNormalize = !!value.id?.trim();

  const handleNormalize = async () => {
    if (!canNormalize) return;
    setNorm({ status: 'loading' });
    try {
      const body = useNameResolver
        ? { name: value.id }
        : { namespace: idTypeValue, chemical_id: value.id };

      const res = await fetch('/normalize-chemical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        setNorm({ status: 'error', message: data.details || 'Normalization failed' });
        return;
      }
      setNorm({
        status: 'done',
        result: data.result as NormResult,
        imageB64: data.structure_image_b64 ?? null,
      });
    } catch {
      setNorm({ status: 'error', message: 'Network error — is the server running?' });
    }
  };

  const handleAccept = () => {
    if (norm.status === 'done' && norm.result.primary_id) {
      onChange({ ...value, name: norm.result.primary_id });
    }
  };

  // Synonyms: unique non-null labels from equivalent_identifiers, excluding primary label
  const synonyms: string[] =
    norm.status === 'done'
      ? Array.from(
          new Set(
            norm.result.equivalent_identifiers
              .map((eq) => eq.label)
              .filter((l): l is string => !!l && l !== norm.result.label)
          )
        )
      : [];

  return (
    <div className="col-12" style={{ display: 'flex', gap: '16px' }}>
      {/* ── Left: inputs ── */}
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 'var(--gap, 10px)' }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
          <div style={{ flex: '0 0 42%' }}>
            <Select
              label="ID Type"
              value={idTypeValue}
              onChange={(e) => applyChange({ idType: e.target.value as SubstanceIdType })}
              options={SUBSTANCE_IDTYPE_OPTIONS}
              style={{ height: '34px', boxSizing: 'border-box' }}
            />
          </div>
          <div style={{ flex: 1, display: 'flex', gap: '6px', alignItems: 'flex-end' }}>
            <div style={{ flex: 1 }}>
              <Input
                label={useNameResolver ? 'Name' : 'Identifier'}
                placeholder={useNameResolver ? 'e.g., ethanol' : 'e.g., 16236'}
                value={value.id || ''}
                onChange={(e) => applyChange({ id: e.target.value })}
                style={{ height: '34px', boxSizing: 'border-box' }}
              />
            </div>
            <button
              type="button"
              onClick={handleNormalize}
              disabled={!canNormalize || norm.status === 'loading'}
              style={{ height: '34px', padding: '0 12px', boxSizing: 'border-box', flexShrink: 0, fontSize: '14px', whiteSpace: 'nowrap' }}
            >
              {norm.status === 'loading' ? 'Looking up…' : 'Find chemical ↗'}
            </button>
          </div>
        </div>

        <Input
          label="Standardized ID"
          placeholder="Accepted standardized identifier"
          tooltip={EXPOSURE_SUBSTANCE}
          value={value.name || ''}
          onChange={(e) => applyChange({ name: e.target.value })}
        />

        {norm.status === 'error' && (
          <div style={{ color: '#c00', fontSize: '0.85rem' }}>{norm.message}</div>
        )}
      </div>

      {/* ── Right: suggested result ── */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {norm.status === 'done' && (
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.8rem', color: '#555', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Suggested Result
            </div>
            {norm.result.normalized ? (
              <div style={{
                border: '1px solid #d0e8d0',
                borderRadius: '6px',
                padding: '10px 14px',
                background: '#f6fbf6',
              }}>
                {/* Image + primary info */}
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
                  {norm.imageB64 && (
                    <img
                      src={`data:image/png;base64,${norm.imageB64}`}
                      alt="Chemical structure"
                      style={{ width: 100, height: 100, flexShrink: 0, border: '1px solid #ddd', borderRadius: '4px', background: '#fff' }}
                    />
                  )}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{norm.result.primary_id}</div>
                    <div style={{ fontSize: '0.82rem', color: '#444', marginTop: '2px' }}>{norm.result.label}</div>
                    {norm.result.description && (
                      <div style={{ fontSize: '0.78rem', color: '#666', marginTop: '4px' }}>
                        {norm.result.description.length > 160
                          ? norm.result.description.slice(0, 160) + '…'
                          : norm.result.description}
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={handleAccept}
                      style={{ marginTop: '8px', padding: '3px 10px', fontSize: '0.82rem' }}
                    >
                      ← Use {norm.result.primary_id}
                    </button>
                  </div>
                </div>

                {/* Synonyms */}
                {synonyms.length > 0 && (
                  <div style={{ marginTop: '8px' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#666', marginBottom: '4px' }}>Synonyms</div>
                    <div style={{ fontSize: '0.78rem', color: '#555', lineHeight: '1.6' }}>
                      {synonyms.join(' · ')}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: '#888', fontSize: '0.85rem' }}>
                No match found for this identifier in NodeNorm.
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
