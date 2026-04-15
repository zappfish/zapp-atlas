import React, { useState, useEffect, useRef } from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import { EXPOSURE_SUBSTANCE } from './explanations';
import { SUBSTANCE_IDTYPE_OPTIONS } from './constants';
import { SubstanceIdType } from '@/schema';

type Substance = {
  name?: string;
  idType: SubstanceIdType;
  id?: string;
  concentration?: string;
  cas_number?: string;
  manufacturer?: string;
  comment?: string;
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

type NormResultItem = {
  queried_id: string;
  result: NormResult;
  imageB64: string | null;
};

type NormState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'done'; items: NormResultItem[]; mode: 'id' | 'name' };

type AcSuggestion = { name: string; chebi_ids: string[]; normalized: NormResult | null };
type AcState = { status: 'idle' } | { status: 'open'; suggestions: AcSuggestion[] };

const HEIGHT = { height: '34px', boxSizing: 'border-box' as const };

// Namespaces that can be resolved to a structure image via /normalize-chemical.
const VIS_NAMESPACES = ['PUBCHEM.COMPOUND', 'INCHIKEY', 'SMILES'];

// Map NodeNorm CURIE prefixes → identifiers.org prefixes where they differ.
const IDENTIFIERS_ORG_PREFIX: Record<string, string> = {
  UniProtKB: 'uniprot',
};

function toIdentifiersOrgUrl(primaryId: string): string {
  const colon = primaryId.indexOf(':');
  if (colon === -1) return `https://identifiers.org/${primaryId}`;
  const prefix = primaryId.slice(0, colon);
  const local = primaryId.slice(colon + 1);
  const mapped = IDENTIFIERS_ORG_PREFIX[prefix] ?? prefix;
  return `https://identifiers.org/${mapped}:${local}`;
}

function ResultCard({ item, onAccept }: { item: NormResultItem; onAccept: () => void }) {
  const [img, setImg] = useState<string | null>(item.imageB64);

  useEffect(() => {
    if (img) return;
    // Find the first equivalent identifier whose namespace can produce an image.
    const visCurie = item.result.equivalent_identifiers
      .map((eq) => eq.identifier)
      .filter((id): id is string => {
        if (!id) return false;
        const ns = id.split(':')[0];
        return VIS_NAMESPACES.includes(ns);
      })[0];
    if (!visCurie) return;

    const colonIdx = visCurie.indexOf(':');
    const ns = visCurie.slice(0, colonIdx);
    const id = visCurie.slice(colonIdx + 1);

    let cancelled = false;
    fetch('/normalize-chemical', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ namespace: ns, chemical_id: id }),
    })
      .then((r) => r.json())
      .then((data) => { if (!cancelled && data.structure_image_b64) setImg(data.structure_image_b64); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [item.result.primary_id]);

  const synonyms = Array.from(new Set(
    item.result.equivalent_identifiers
      .map((eq) => eq.label)
      .filter((l): l is string => !!l && l !== item.result.label)
  )).slice(0, 4);

  return (
    <div style={{ border: '1px solid #d0e8d0', borderRadius: '5px', padding: '7px 10px', background: '#f6fbf6' }}>
      {/* Info (left) + image (right) */}
      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', flexWrap: 'wrap' }}>
            <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>{item.result.primary_id}</span>
            <span style={{ fontSize: '0.8rem', color: '#444' }}>{item.result.label}</span>
          </div>
          {item.result.description && (
            <div style={{ fontSize: '0.74rem', color: '#666', marginTop: '2px', lineHeight: 1.4 }}>
              {item.result.description.length > 100
                ? item.result.description.slice(0, 100) + '…'
                : item.result.description}
            </div>
          )}
          {synonyms.length > 0 && (
            <div style={{ fontSize: '0.72rem', color: '#777', marginTop: '3px' }}>
              {synonyms.join(' · ')}
            </div>
          )}
        </div>
        {img && (
          <img
            src={`data:image/png;base64,${img}`}
            alt="Chemical structure"
            style={{ width: 60, height: 60, flexShrink: 0, border: '1px solid #ddd', borderRadius: '3px', background: '#fff' }}
          />
        )}
      </div>
      {/* Buttons: Use (left) | Source (right) */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px' }}>
        <button type="button" onClick={onAccept} style={{ padding: '2px 8px', fontSize: '0.75rem' }}>
          Use {item.result.primary_id}
        </button>
        {item.result.primary_id && (
          <a
            href={toIdentifiersOrgUrl(item.result.primary_id)}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: '2px 8px',
              fontSize: '0.75rem',
              border: '1px solid #bbb',
              borderRadius: '3px',
              background: '#fff',
              color: '#333',
              textDecoration: 'none',
              display: 'inline-block',
            }}
          >
            Take me to the source ↗
          </a>
        )}
      </div>
    </div>
  );
}

export default function SubstanceFields({
  value,
  onChange,
  acLimit = 5,
}: {
  value: Substance;
  onChange: (next: Substance) => void;
  /** Max autocomplete suggestions to show (default: 5). */
  acLimit?: number;
}) {
  const [norm, setNorm] = useState<NormState>({ status: 'idle' });
  const [ac, setAc] = useState<AcState>({ status: 'idle' });
  const [acceptedEquivIds, setAcceptedEquivIds] = useState<EqIdentifier[]>([]);
  const acTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const idTypeValue: SubstanceIdType = value.idType ?? 'None';
  const useNameResolver = idTypeValue === 'None';
  const canNormalize = !!value.id?.trim();

  const applyChange = (partial: Partial<Substance>) => {
    onChange({ ...value, ...partial });
    if ('id' in partial || 'idType' in partial) {
      setNorm({ status: 'idle' });
      setAcceptedEquivIds([]);
    }
    if ('idType' in partial) {
      setAc({ status: 'idle' });
    }
  };

  // Autocomplete: debounced fetch when in name mode and ≥2 chars
  useEffect(() => {
    if (!useNameResolver || !value.id || value.id.length < 2) {
      setAc({ status: 'idle' });
      return;
    }
    if (acTimerRef.current) clearTimeout(acTimerRef.current);
    acTimerRef.current = setTimeout(async () => {
      try {
        const res = await fetch(`/autocomplete-chemical?q=${encodeURIComponent(value.id!)}&limit=${acLimit}`);
        const suggestions: AcSuggestion[] = await res.json();
        setAc(suggestions.length > 0 ? { status: 'open', suggestions } : { status: 'idle' });
      } catch {
        setAc({ status: 'idle' });
      }
    }, 200);
    return () => { if (acTimerRef.current) clearTimeout(acTimerRef.current); };
  }, [value.id, useNameResolver]);

  const normFetch = async (body: object, queriedId: string): Promise<NormResultItem | null> => {
    try {
      const res = await fetch('/normalize-chemical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) return null;
      return { queried_id: queriedId, result: data.result as NormResult, imageB64: data.structure_image_b64 ?? null };
    } catch {
      return null;
    }
  };

  // Returns all deduplicated results from a single /normalize-chemical response.
  // Uses data.results (array) when present; falls back to data.result.
  const normFetchAll = async (body: object): Promise<NormResultItem[]> => {
    try {
      const res = await fetch('/normalize-chemical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) return [];
      const list: NormResult[] = Array.isArray(data.results) && data.results.length > 0
        ? data.results
        : data.result?.normalized ? [data.result] : [];
      return list
        .filter((r) => r.normalized)
        .map((r, i) => ({
          queried_id: r.primary_id ?? String(i),
          result: r,
          imageB64: i === 0 ? (data.structure_image_b64 ?? null) : null,
        }));
    } catch {
      return [];
    }
  };

  // Fire ChEBI lookups + name resolver in parallel, dedupe by primary_id.
  const lookupByName = async (name: string, knownChebiIds?: string[]): Promise<NormResultItem[]> => {
    let chebiIds = knownChebiIds;
    if (!chebiIds) {
      try {
        const res = await fetch(`/autocomplete-chemical?q=${encodeURIComponent(name)}&limit=${acLimit}`);
        const suggestions: AcSuggestion[] = await res.json();
        const exact = suggestions.find((s) => s.name.toLowerCase() === name.toLowerCase());
        chebiIds = exact?.chebi_ids ?? [];
      } catch {
        chebiIds = [];
      }
    }
    const chebiCalls = chebiIds.map((fullId) =>
      normFetch({ namespace: 'CHEBI', chemical_id: fullId.replace('CHEBI:', '') }, fullId)
    );
    const [chebiResults, nameResults] = await Promise.all([
      Promise.all(chebiCalls).then((rs) => rs.filter((r): r is NormResultItem => r !== null && r.result.normalized)),
      normFetchAll({ name }),
    ]);
    const seen = new Set<string>();
    return [...chebiResults, ...nameResults].filter((r) => {
      const pid = r.result.primary_id ?? r.queried_id;
      if (seen.has(pid)) return false;
      seen.add(pid);
      return true;
    });
  };

  const handleSuggestionClick = async (suggestion: AcSuggestion) => {
    applyChange({ id: suggestion.name });
    setAc({ status: 'idle' });
    // Use precomputed NodeNorm data when available — avoids a live API round-trip.
    if (suggestion.normalized?.normalized) {
      setNorm({
        status: 'done',
        items: [{
          queried_id: suggestion.chebi_ids[0] ?? suggestion.name,
          result: suggestion.normalized,
          imageB64: null,
        }],
        mode: 'name',
      });
    } else {
      setNorm({ status: 'loading' });
      const items = await lookupByName(suggestion.name, suggestion.chebi_ids);
      setNorm(items.length > 0 ? { status: 'done', items, mode: 'name' } : { status: 'error', message: 'No results found in NodeNorm.' });
    }
  };

  // Button click: name mode uses shared lookup; ID mode is a single call
  const handleNormalize = async () => {
    if (!canNormalize) return;
    setAc({ status: 'idle' });
    setNorm({ status: 'loading' });
    try {
      if (useNameResolver) {
        const items = await lookupByName(value.id!);
        setNorm(items.length > 0 ? { status: 'done', items, mode: 'name' } : { status: 'error', message: 'No results found.' });
      } else {
        const data = await normFetch({ namespace: idTypeValue, chemical_id: value.id }, `${idTypeValue}:${value.id}`);
        if (!data) { setNorm({ status: 'error', message: 'Normalization failed' }); return; }
        setNorm({ status: 'done', items: [data], mode: 'id' });
      }
    } catch {
      setNorm({ status: 'error', message: 'Network error — is the server running?' });
    }
  };

  const handleAccept = (item: NormResultItem) => {
    if (item.result.primary_id) {
      onChange({ ...value, name: item.result.primary_id });
      setAcceptedEquivIds(item.result.equivalent_identifiers);
    }
  };


  return (
    <div className="col-12" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>

      {/* ── Row 1: ID Type + input + button ── */}
      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
        <div style={{ flex: '0 0 38%' }}>
          <Select
            label="ID Type"
            value={idTypeValue}
            onChange={(e) => applyChange({ idType: e.target.value as SubstanceIdType })}
            options={SUBSTANCE_IDTYPE_OPTIONS}
            style={HEIGHT}
          />
        </div>
        <div style={{ flex: 1, position: 'relative' }}>
          <Input
            label={useNameResolver ? 'Name' : 'Identifier'}
            placeholder={useNameResolver ? 'e.g., ethanol' : 'e.g., 16236'}
            value={value.id || ''}
            onChange={(e) => applyChange({ id: e.target.value })}
            onBlur={() => setTimeout(() => setAc({ status: 'idle' }), 150)}
            style={HEIGHT}
          />
          {ac.status === 'open' && (
            <ul style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              zIndex: 100,
              margin: 0,
              padding: 0,
              listStyle: 'none',
              border: '1px solid #ccc',
              borderRadius: '4px',
              background: '#fff',
              boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
              maxHeight: '220px',
              overflowY: 'auto',
            }}>
              {ac.suggestions.map((s) => (
                <li
                  key={s.name}
                  onMouseDown={() => handleSuggestionClick(s)}
                  style={{
                    padding: '7px 10px',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderBottom: '1px solid #f0f0f0',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = '#f5f5f5')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = '')}
                >
                  <span>{s.name}</span>
                  {s.chebi_ids.length > 1 && (
                    <span style={{ fontSize: '0.72rem', color: '#888', marginLeft: '8px', flexShrink: 0 }}>
                      {s.chebi_ids.length} IDs
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
        <button
          type="button"
          onClick={handleNormalize}
          disabled={!canNormalize || norm.status === 'loading'}
          style={{ ...HEIGHT, padding: '0 12px', flexShrink: 0, fontSize: '14px', whiteSpace: 'nowrap' }}
        >
          {norm.status === 'loading' ? 'Looking up…' : 'Find chemical ↗'}
        </button>
      </div>

      {/* ── Row 2: Suggested results (left) | Standardized fields (right) ── */}
      <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>

        {/* Left: suggested results */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {norm.status === 'error' && (
            <div style={{ color: '#c00', fontSize: '0.82rem', marginTop: '2px' }}>{norm.message}</div>
          )}
          {norm.status === 'done' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {/* Result cards */}
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.75rem', color: '#555', marginBottom: '5px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Suggested Result{norm.items.length > 1 ? `s (${norm.items.length})` : ''}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {norm.items.map((item, idx) =>
                    item.result.normalized ? (
                      <ResultCard key={idx} item={item} onAccept={() => handleAccept(item)} />
                    ) : (
                      <div key={idx} style={{ color: '#888', fontSize: '0.82rem' }}>
                        No match for {item.queried_id}
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Equivalent identifiers table — ID queries only */}
              {norm.mode === 'id' && norm.items[0]?.result.equivalent_identifiers.length > 0 && (
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.75rem', color: '#555', marginBottom: '5px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Equivalent Identifiers ({norm.items[0].result.equivalent_identifiers.length})
                  </div>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #d0d0d0', background: '#f5f5f5' }}>
                        <th style={{ textAlign: 'left', padding: '4px 8px', fontWeight: 600, color: '#444', width: '48%' }}>Identifier</th>
                        <th style={{ textAlign: 'left', padding: '4px 8px', fontWeight: 600, color: '#444' }}>Name / Label</th>
                      </tr>
                    </thead>
                    <tbody>
                      {norm.items[0].result.equivalent_identifiers.map((eq, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid #ececec', background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                          <td style={{ padding: '3px 8px', fontFamily: 'monospace', color: '#333' }}>{eq.identifier}</td>
                          <td style={{ padding: '3px 8px', color: '#555' }}>{eq.label ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: standardized ID + concentration + comment */}
        <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <Input
            label="Standardized ID"
            placeholder="Accepted standardized identifier"
            tooltip={EXPOSURE_SUBSTANCE}
            value={value.name || ''}
            onChange={(e) => applyChange({ name: e.target.value })}
          />
          <Input
            label="Concentration"
            placeholder="e.g. 10 μM"
            value={value.concentration || ''}
            onChange={(e) => applyChange({ concentration: e.target.value })}
          />
          <Input
            label="CAS Number"
            placeholder="e.g. 64-17-5"
            value={value.cas_number || ''}
            onChange={(e) => applyChange({ cas_number: e.target.value })}
          />
          <Input
            label="Manufacturer"
            placeholder="e.g. Sigma-Aldrich"
            value={value.manufacturer || ''}
            onChange={(e) => applyChange({ manufacturer: e.target.value })}
          />
          <Input
            label="Comment"
            placeholder="Optional note about this substance"
            value={value.comment || ''}
            onChange={(e) => applyChange({ comment: e.target.value })}
          />
          {acceptedEquivIds.length > 0 && (
            <div style={{ marginTop: '2px' }}>
              <div style={{ fontWeight: 600, fontSize: '0.75rem', color: '#555', marginBottom: '5px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Equivalent Identifiers ({acceptedEquivIds.length})
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #d0d0d0', background: '#f5f5f5' }}>
                    <th style={{ textAlign: 'left', padding: '4px 8px', fontWeight: 600, color: '#444', width: '48%' }}>Identifier</th>
                    <th style={{ textAlign: 'left', padding: '4px 8px', fontWeight: 600, color: '#444' }}>Name / Label</th>
                  </tr>
                </thead>
                <tbody>
                  {acceptedEquivIds.map((eq, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #ececec', background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                      <td style={{ padding: '3px 8px', fontFamily: 'monospace', color: '#333' }}>{eq.identifier}</td>
                      <td style={{ padding: '3px 8px', color: '#555' }}>{eq.label ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
