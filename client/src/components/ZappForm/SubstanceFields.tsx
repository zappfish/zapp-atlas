import React, { useState } from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import { EXPOSURE_SUBSTANCE } from './explanations';

type Substance = {
  name?: string;
  idType: 'PubChem' | 'CAS' | 'ChEBI' | 'None';
  id?: string;
  // Resolved fields populated by normalization
  resolvedChebiIds?: string[];
  resolvedPubchemCids?: string[];
  resolvedSynonyms?: string[];
  normalized?: boolean;
};

type LookupStatus = 'idle' | 'loading' | 'found' | 'not_found' | 'unavailable' | 'error';

const ID_TYPE_OPTIONS: Array<{ value: Substance['idType']; label: string }> = [
  { value: 'CAS', label: 'CAS' },
  { value: 'PubChem', label: 'PubChem' },
  { value: 'ChEBI', label: 'ChEBI' },
  { value: 'None', label: 'None' }
];

async function lookupChemical(query: string): Promise<{ found: boolean; entry?: Record<string, unknown>; error?: string }> {
  const res = await fetch(`/normalize/chemical?q=${encodeURIComponent(query)}`);
  if (res.status === 503) return { found: false, error: 'unavailable' };
  if (!res.ok) return { found: false, error: 'error' };
  const data = await res.json();
  if (data.error) return { found: false, error: data.error };
  return { found: data.found, entry: data.found ? data : undefined };
}

export default function SubstanceFields({
  value,
  onChange
}: {
  value: Substance;
  onChange: (next: Substance) => void;
}) {
  const [lookupStatus, setLookupStatus] = useState<LookupStatus>('idle');
  const [lookupMessage, setLookupMessage] = useState<string>('');

  const applyChange = (partial: Partial<Substance>) => {
    onChange({ ...value, ...partial });
  };

  const idTypeValue: Substance['idType'] = value.idType ?? 'CAS';

  const handleLookup = async () => {
    const query = (value.name || value.id || '').trim();
    if (!query) return;

    setLookupStatus('loading');
    setLookupMessage('');

    try {
      const result = await lookupChemical(query);

      if (result.error === 'unavailable') {
        setLookupStatus('unavailable');
        setLookupMessage('Chemical index not yet available — run the pipeline first.');
        return;
      }
      if (result.error) {
        setLookupStatus('error');
        setLookupMessage('Lookup failed. Check that the server is running.');
        return;
      }
      if (!result.found || !result.entry) {
        setLookupStatus('not_found');
        setLookupMessage(`"${query}" not found in chemical index.`);
        return;
      }

      const entry = result.entry as {
        cas_number: string;
        chebi_ids: string[];
        pubchem_cids: string[];
        synonyms: string[];
      };

      // Auto-fill: prefer ChEBI as the canonical ID type
      const chebiId = entry.chebi_ids?.[0];
      const resolvedId = chebiId ?? entry.cas_number ?? '';
      const resolvedIdType: Substance['idType'] = chebiId ? 'ChEBI' : 'CAS';

      onChange({
        ...value,
        id: resolvedId,
        idType: resolvedIdType,
        resolvedChebiIds: entry.chebi_ids,
        resolvedPubchemCids: entry.pubchem_cids,
        resolvedSynonyms: entry.synonyms,
        normalized: true,
      });

      setLookupStatus('found');
      setLookupMessage(
        `Resolved → ChEBI: ${entry.chebi_ids.join(', ') || 'none'} | CAS: ${entry.cas_number}`
      );
    } catch {
      setLookupStatus('error');
      setLookupMessage('Lookup failed. Check that the server is running.');
    }
  };

  const statusColor: Record<LookupStatus, string> = {
    idle: '',
    loading: '#888',
    found: '#2a7a2a',
    not_found: '#b05000',
    unavailable: '#888',
    error: '#c00',
  };

  return (
    <>
      <div className="col-6" style={{ display: 'flex', gap: '6px', alignItems: 'flex-end' }}>
        <div style={{ flex: 1 }}>
          <Input
            label="Substance"
            placeholder="Substance label or CAS number"
            tooltip={EXPOSURE_SUBSTANCE}
            value={value.name || ''}
            onChange={(e) => {
              applyChange({ name: e.target.value, normalized: false });
              setLookupStatus('idle');
              setLookupMessage('');
            }}
          />
        </div>
        <button
          type="button"
          onClick={handleLookup}
          disabled={lookupStatus === 'loading' || !(value.name || value.id)}
          style={{
            marginBottom: '2px',
            padding: '0 10px',
            height: '32px',
            fontSize: '12px',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
          }}
        >
          {lookupStatus === 'loading' ? '...' : 'Normalize'}
        </button>
      </div>
      <div className="col-2">
        <Select
          label="ID Type"
          value={idTypeValue}
          onChange={(e) => applyChange({ idType: e.target.value as Substance['idType'] })}
          options={ID_TYPE_OPTIONS}
        />
      </div>
      <div className="col-4">
        <Input
          label="Identifier"
          placeholder="e.g., 50-00-0"
          value={value.id || ''}
          onChange={(e) => applyChange({ id: e.target.value })}
        />
      </div>
      {lookupMessage && (
        <div className="col-12" style={{ fontSize: '12px', color: statusColor[lookupStatus], marginTop: '-6px' }}>
          {lookupMessage}
        </div>
      )}
    </>
  );
}
