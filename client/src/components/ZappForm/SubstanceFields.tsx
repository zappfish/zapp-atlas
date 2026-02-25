import React, { useState } from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import { EXPOSURE_SUBSTANCE } from './explanations';

type IdType = 'PubChem' | 'CAS' | 'ChEBI' | 'None';

export type Substance = {
  name?: string;
  idType: IdType;
  id?: string;
  // Populated after normalization
  resolvedNamespace?: 'ChEBI' | 'PubChem' | null;
  resolvedId?: string | null;
  confidence?: 'high' | 'medium' | 'low' | null;
  allChebiIds?: string[];
  allPubchemCids?: string[];
  casNumber?: string;
  normalized?: boolean;
};

type NormalizeStatus = 'idle' | 'loading' | 'high' | 'medium' | 'low' | 'not_found' | 'unavailable' | 'error';

const ID_TYPE_OPTIONS: Array<{ value: IdType; label: string }> = [
  { value: 'CAS', label: 'CAS' },
  { value: 'PubChem', label: 'PubChem' },
  { value: 'ChEBI', label: 'ChEBI' },
  { value: 'None', label: 'None' }
];

// Maps Substance['idType'] to the id_type value the server expects
const ID_TYPE_SERVER: Record<IdType, string> = {
  CAS: 'CAS',
  PubChem: 'PubChem',
  ChEBI: 'ChEBI',
  None: '',
};

async function fetchNormalization(idType: IdType, id: string) {
  const params = new URLSearchParams({ id_type: ID_TYPE_SERVER[idType], id });
  const res = await fetch(`/normalize/chemical?${params}`);
  if (res.status === 503) return { error: 'unavailable' as const };
  if (!res.ok) return { error: 'error' as const };
  return res.json();
}

export default function SubstanceFields({
  value,
  onChange
}: {
  value: Substance;
  onChange: (next: Substance) => void;
}) {
  const [status, setStatus] = useState<NormalizeStatus>('idle');
  const [message, setMessage] = useState('');

  const idTypeValue: IdType = value.idType ?? 'CAS';
  const canNormalize = idTypeValue !== 'None' && !!(value.id?.trim());

  const applyChange = (partial: Partial<Substance>) => {
    onChange({ ...value, ...partial });
  };

  const resetNormalization = () => {
    setStatus('idle');
    setMessage('');
  };

  const handleNormalize = async () => {
    if (!canNormalize) return;
    setStatus('loading');
    setMessage('');

    try {
      const data = await fetchNormalization(idTypeValue, value.id!.trim());

      if (data.error === 'unavailable') {
        setStatus('unavailable');
        setMessage('Chemical index not yet available.');
        return;
      }
      if (data.error) {
        setStatus('error');
        setMessage('Lookup failed — is the server running?');
        return;
      }
      if (!data.found) {
        setStatus('not_found');
        setMessage(`${idTypeValue} "${value.id}" not found in chemical index.`);
        return;
      }

      // Update form: set idType + id to the resolved canonical values
      const resolvedIdType: IdType = data.resolved_namespace === 'ChEBI' ? 'ChEBI'
                                    : data.resolved_namespace === 'PubChem' ? 'PubChem'
                                    : idTypeValue;

      onChange({
        ...value,
        idType: data.resolved_id ? resolvedIdType : idTypeValue,
        id: data.resolved_id ?? value.id,
        resolvedNamespace: data.resolved_namespace ?? null,
        resolvedId: data.resolved_id ?? null,
        confidence: data.confidence ?? null,
        allChebiIds: data.chebi_ids ?? [],
        allPubchemCids: data.pubchem_cids ?? [],
        casNumber: data.cas_number ?? undefined,
        normalized: true,
      });

      const conf: NormalizeStatus = data.confidence === 'high' ? 'high'
                                  : data.confidence === 'medium' ? 'medium'
                                  : 'low';
      setStatus(conf);

      if (data.resolved_namespace && data.resolved_id) {
        const fallbackNote = data.resolved_namespace === 'PubChem'
          ? '  (no unique ChEBI mapping — using PubChem as fallback)'
          : '';
        setMessage(`→ ${data.resolved_namespace}: ${data.resolved_id}${fallbackNote}`);
      } else {
        setMessage('No unique identifier found — try entering the ID directly in a different namespace.');
      }
    } catch {
      setStatus('error');
      setMessage('Lookup failed — is the server running?');
    }
  };

  const statusColor: Record<NormalizeStatus, string> = {
    idle: '',
    loading: '#888',
    high: '#2a7a2a',
    medium: '#7a6a00',
    low: '#b05000',
    not_found: '#b05000',
    unavailable: '#888',
    error: '#c00',
  };

  return (
    <>
      <div className="col-6">
        <Input
          label="Substance"
          placeholder="Substance name"
          tooltip={EXPOSURE_SUBSTANCE}
          value={value.name || ''}
          onChange={(e) => applyChange({ name: e.target.value })}
        />
      </div>
      <div className="col-2">
        <Select
          label="ID Type"
          value={idTypeValue}
          onChange={(e) => {
            applyChange({ idType: e.target.value as IdType, normalized: false });
            resetNormalization();
          }}
          options={ID_TYPE_OPTIONS}
        />
      </div>
      <div className="col-4" style={{ display: 'flex', gap: '6px', alignItems: 'flex-end' }}>
        <div style={{ flex: 1 }}>
          <Input
            label="Identifier"
            placeholder={
              idTypeValue === 'CAS' ? 'e.g. 64-17-5'
              : idTypeValue === 'PubChem' ? 'e.g. 702'
              : idTypeValue === 'ChEBI' ? 'e.g. CHEBI:16236'
              : '—'
            }
            value={value.id || ''}
            onChange={(e) => {
              applyChange({ id: e.target.value, normalized: false });
              resetNormalization();
            }}
          />
        </div>
        {idTypeValue !== 'None' && (
          <button
            type="button"
            onClick={handleNormalize}
            disabled={status === 'loading' || !canNormalize}
            title="Resolve to canonical ChEBI or PubChem ID"
            style={{
              marginBottom: '2px',
              padding: '0 10px',
              height: '32px',
              fontSize: '12px',
              cursor: canNormalize ? 'pointer' : 'default',
              whiteSpace: 'nowrap',
            }}
          >
            {status === 'loading' ? '…' : 'Normalize'}
          </button>
        )}
      </div>
      {message && (
        <div className="col-12" style={{ fontSize: '12px', color: statusColor[status], marginTop: '-4px' }}>
          {message}
        </div>
      )}
    </>
  );
}
