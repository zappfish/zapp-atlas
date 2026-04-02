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
  const canNormalize = idTypeValue !== 'None' && !!value.id?.trim();

  const handleNormalize = async () => {
    if (!canNormalize) return;
    setNorm({ status: 'loading' });
    try {
      const res = await fetch('/normalize-chemical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ namespace: idTypeValue, chemical_id: value.id }),
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

  return (
    <>
      <div className="col-6">
        <Input
          label="Substance"
          placeholder="Substance label"
          tooltip={EXPOSURE_SUBSTANCE}
          value={value.name || ''}
          onChange={(e) => applyChange({ name: e.target.value })}
        />
      </div>
      <div className="col-2">
        <Select
          label="ID Type"
          value={idTypeValue}
          onChange={(e) => applyChange({ idType: e.target.value as SubstanceIdType })}
          options={SUBSTANCE_IDTYPE_OPTIONS}
        />
      </div>
      <div className="col-4">
        <div style={{ display: 'flex', gap: '6px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <Input
              label="Identifier"
              placeholder="e.g., 16236"
              value={value.id || ''}
              onChange={(e) => applyChange({ id: e.target.value })}
            />
          </div>
          <button
            type="button"
            onClick={handleNormalize}
            disabled={!canNormalize || norm.status === 'loading'}
            style={{ padding: '6px 10px', marginBottom: '1px', whiteSpace: 'nowrap', flexShrink: 0 }}
          >
            {norm.status === 'loading' ? 'Looking up…' : 'Normalize ↗'}
          </button>
        </div>
      </div>

      {norm.status === 'error' && (
        <div className="col-12" style={{ color: '#c00', fontSize: '0.85rem', marginTop: '4px' }}>
          {norm.message}
        </div>
      )}

      {norm.status === 'done' && (
        <div className="col-12" style={{ marginTop: '6px' }}>
          {norm.result.normalized ? (
            <div style={{
              border: '1px solid #d0e8d0',
              borderRadius: '6px',
              padding: '10px 14px',
              background: '#f6fbf6',
            }}>
              {/* Header row: image + primary ID + accept button */}
              <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start', marginBottom: '10px' }}>
                {norm.imageB64 && (
                  <img
                    src={`data:image/png;base64,${norm.imageB64}`}
                    alt="Chemical structure"
                    style={{ width: 110, height: 110, flexShrink: 0, border: '1px solid #ddd', borderRadius: '4px', background: '#fff' }}
                  />
                )}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '1rem' }}>{norm.result.primary_id}</div>
                  <div style={{ fontSize: '0.82rem', color: '#555', marginTop: '2px' }}>{norm.result.label}</div>
                  {norm.result.description && (
                    <div style={{ fontSize: '0.78rem', color: '#666', marginTop: '4px' }}>
                      {norm.result.description.length > 180
                        ? norm.result.description.slice(0, 180) + '…'
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

              {/* Equivalent identifiers table */}
              {norm.result.equivalent_identifiers.length > 0 && (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
                    <thead>
                      <tr style={{ background: '#e6f4e6', textAlign: 'left' }}>
                        <th style={{ padding: '4px 8px', borderBottom: '1px solid #c8e0c8', fontWeight: 600 }}>Identifier</th>
                        <th style={{ padding: '4px 8px', borderBottom: '1px solid #c8e0c8', fontWeight: 600 }}>Label</th>
                      </tr>
                    </thead>
                    <tbody>
                      {norm.result.equivalent_identifiers.map((eq, i) => (
                        <tr key={i} style={{ background: i % 2 === 0 ? '#fff' : '#f0f8f0' }}>
                          <td style={{ padding: '3px 8px', fontFamily: 'monospace', color: '#333' }}>{eq.identifier}</td>
                          <td style={{ padding: '3px 8px', color: '#555' }}>{eq.label ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
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
    </>
  );
}
