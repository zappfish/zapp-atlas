import React, { useState, useEffect, useRef } from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import { EXPOSURE_SUBSTANCE } from './explanations';
import { SUBSTANCE_IDTYPE_OPTIONS, VEHICLE_OPTIONS, MANUFACTURER_OPTIONS, CONC_UNIT_OPTIONS } from './constants';
import { SubstanceIdType } from '@/schema';

type Substance = {
  chemical_id?: string;
  unrecognized_chemical_name?: string;
  synonym?: string[];
  idType: SubstanceIdType;
  id?: string;
  concentration?: number | null;
  concentration_unit?: string;
  cas_id?: string;
  manufacturer?: string;
  vehicle_type?: string;
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

const VIS_NAMESPACES = ['PUBCHEM.COMPOUND', 'INCHIKEY', 'SMILES'];
const IDENTIFIERS_ORG_PREFIX: Record<string, string> = { UniProtKB: 'uniprot' };
const RESULTS_HEIGHT = 340;
const CARD_HEIGHT = 150; // px — uniform height for all result cards

function toIdentifiersOrgUrl(primaryId: string): string {
  const colon = primaryId.indexOf(':');
  if (colon === -1) return `https://identifiers.org/${primaryId}`;
  const prefix = primaryId.slice(0, colon);
  const local = primaryId.slice(colon + 1);
  return `https://identifiers.org/${IDENTIFIERS_ORG_PREFIX[prefix] ?? prefix}:${local}`;
}

function ResultCard({
  item,
  onAccept,
  hideAccept = false,
}: {
  item: NormResultItem;
  onAccept: () => void;
  hideAccept?: boolean;
}) {
  const [img, setImg] = useState<string | null>(item.imageB64);

  useEffect(() => {
    if (img) return;
    const visCurie = item.result.equivalent_identifiers
      .map((eq) => eq.identifier)
      .filter((id): id is string => !!id && VIS_NAMESPACES.includes(id.split(':')[0] as string))[0];
    if (!visCurie) return;
    const colonIdx = visCurie.indexOf(':');
    let cancelled = false;
    fetch('/api/chemicals/normalize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ namespace: visCurie.slice(0, colonIdx), chemical_id: visCurie.slice(colonIdx + 1) }),
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

  const equivIds = item.result.equivalent_identifiers;

  return (
    <div style={{
      border: '1px solid #d0e8d0',
      borderRadius: '5px',
      padding: '9px 12px',
      background: '#f6fbf6',
      display: 'flex',
      gap: '14px',
      alignItems: 'stretch',
      height: `${CARD_HEIGHT}px`,
    }}>

      {/* ── Left 50%: scrollable text + pinned buttons + image filling full height ── */}
      <div style={{ flex: '0 0 50%', display: 'flex', gap: '12px', alignItems: 'stretch' }}>
        {/* Text (scrollable) + buttons (pinned) */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', flexWrap: 'wrap', marginBottom: '2px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>{item.result.primary_id}</span>
              <span style={{ fontSize: '0.8rem', color: '#444' }}>{item.result.label}</span>
            </div>
            {item.result.description && (
              <div style={{ fontSize: '0.73rem', color: '#666', lineHeight: 1.35, marginBottom: '3px' }}>
                {item.result.description.length > 120
                  ? item.result.description.slice(0, 120) + '…'
                  : item.result.description}
              </div>
            )}
            {synonyms.length > 0 && (
              <div style={{ fontSize: '0.71rem', color: '#888' }}>
                {synonyms.join(' · ')}
              </div>
            )}
          </div>
          {!hideAccept && (
            <div style={{ flexShrink: 0, display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap', paddingTop: '6px' }}>
              <button type="button" onClick={onAccept} style={{ padding: '2px 10px', fontSize: '0.75rem' }}>
                Use {item.result.primary_id}
              </button>
              {item.result.primary_id && (
                <a
                  href={toIdentifiersOrgUrl(item.result.primary_id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    padding: '2px 8px', fontSize: '0.75rem',
                    border: '1px solid #bbb', borderRadius: '3px',
                    background: '#fff', color: '#333', textDecoration: 'none',
                  }}
                >
                  Source ↗
                </a>
              )}
            </div>
          )}
        </div>
        {/* Structure image — fills card content height via alignItems: stretch on parent */}
        {img && (
          <img
            src={`data:image/svg+xml;base64,${img}`}
            alt="Chemical structure"
            style={{ height: '100%', width: 'auto', flexShrink: 0, border: '1px solid #ddd', borderRadius: '4px', background: '#fff', objectFit: 'contain' }}
          />
        )}
      </div>

      {/* ── Right: equivalent identifiers, scrollable to fill card height ── */}
      {equivIds.length > 0 && (
        <div style={{ flex: 1, minWidth: 0, borderLeft: '1px solid #d8ecd8', paddingLeft: '12px', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ flexShrink: 0, fontSize: '0.68rem', fontWeight: 700, color: '#6a8a6a', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '4px' }}>
            Equivalent identifiers ({equivIds.length})
          </div>
          <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', minHeight: 0, paddingRight: '2px' }}>
            <table style={{ width: '100%', tableLayout: 'fixed', borderCollapse: 'collapse', fontSize: '0.73rem' }}>
              <colgroup>
                <col style={{ width: '55%' }} />
                <col style={{ width: '45%' }} />
              </colgroup>
              <thead>
                <tr style={{ borderBottom: '1px solid #c8dcc8' }}>
                  <th style={{ padding: '2px 8px 3px 0', textAlign: 'left', fontWeight: 600, color: '#5a7a5a', fontSize: '0.68rem' }}>Identifier</th>
                  <th style={{ padding: '2px 0 3px', textAlign: 'left', fontWeight: 600, color: '#5a7a5a', fontSize: '0.68rem' }}>Name / Label</th>
                </tr>
              </thead>
              <tbody>
                {equivIds.map((eq, i) => (
                  <tr key={i} style={{ borderBottom: i < equivIds.length - 1 ? '1px solid #e8f0e8' : 'none' }}>
                    <td style={{ padding: '2px 8px 2px 0', fontFamily: 'monospace', color: '#333', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {eq.identifier}
                    </td>
                    <td style={{ padding: '2px 0', color: '#555', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {eq.label ?? '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Shared style tokens ──────────────────────────────────────────────────────

const LOOKUP_BAR: React.CSSProperties = {
  background: '#f4f7f4',
  border: '1px solid #d8e8d8',
  borderRadius: '6px',
  padding: '10px 12px',
};

const SECTION_LABEL: React.CSSProperties = {
  fontSize: '0.7rem',
  fontWeight: 700,
  color: '#5a7a5a',
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
  marginBottom: '8px',
};

const BAR_INPUT: React.CSSProperties = {
  width: '100%', height: '34px', fontSize: '0.88rem',
  border: '1px solid #c8c8c8', borderRadius: '4px',
  padding: '0 10px', boxSizing: 'border-box', background: '#fff',
};

const BAR_SELECT: React.CSSProperties = {
  height: '34px', fontSize: '0.85rem',
  border: '1px solid #c8c8c8', borderRadius: '4px',
  padding: '0 6px', boxSizing: 'border-box', background: '#fff',
};

const SECTION_BOX: React.CSSProperties = {
  border: '1px solid #dde8dd',
  borderRadius: '6px',
  padding: '10px 12px',
};

// ── Main component ───────────────────────────────────────────────────────────

export default function SubstanceFields({
  value,
  onChange,
  acLimit = 5,
  mode = 'substance',
}: {
  value: Substance;
  onChange: (next: Substance) => void;
  acLimit?: number;
  mode?: 'substance' | 'vehicle';
}) {
  const [norm, setNorm] = useState<NormState>({ status: 'idle' });
  const [ac, setAc] = useState<AcState>({ status: 'idle' });
  const [infoRevealed, setInfoRevealed] = useState(() => !!value.chemical_id);
  const [otherMfrPending, setOtherMfrPending] = useState(false);
  const acTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const idTypeValue: SubstanceIdType = value.idType ?? 'None';
  const useNameResolver = idTypeValue === 'None';
  const canNormalize = !!value.id?.trim();

  const applyChange = (partial: Partial<Substance>) => {
    onChange({ ...value, ...partial });
    if ('id' in partial || 'idType' in partial || 'vehicle_type' in partial)
      setNorm({ status: 'idle' });
    if ('idType' in partial) setAc({ status: 'idle' });
  };

  // Debounced autocomplete
  useEffect(() => {
    if (!useNameResolver || !value.id || value.id.length < 2) { setAc({ status: 'idle' }); return; }
    if (acTimerRef.current) clearTimeout(acTimerRef.current);
    acTimerRef.current = setTimeout(async () => {
      try {
        const res = await fetch(`/api/chemicals/autocomplete?q=${encodeURIComponent(value.id!)}&limit=${acLimit}`);
        const suggestions: AcSuggestion[] = await res.json();
        setAc(suggestions.length > 0 ? { status: 'open', suggestions } : { status: 'idle' });
      } catch { setAc({ status: 'idle' }); }
    }, 200);
    return () => { if (acTimerRef.current) clearTimeout(acTimerRef.current); };
  }, [value.id, useNameResolver]);

  // Vehicle auto-fetch — also auto-populates standardized ID
  useEffect(() => {
    if (mode !== 'vehicle') return;
    const option = VEHICLE_OPTIONS.find((o) => o.value === value.vehicle_type);
    if (!option?.meaning) { setNorm({ status: 'idle' }); onChange({ ...value, chemical_id: '' }); return; }
    let cancelled = false;
    setNorm({ status: 'loading' });
    fetch(`/api/chemicals/vehicle-info?meaning=${encodeURIComponent(option.meaning)}`)
      .then((r) => r.json())
      .then((data) => {
        if (cancelled) return;
        if (data.found && data.result?.normalized) {
          setNorm({ status: 'done', items: [{ queried_id: option.meaning!, result: data.result, imageB64: data.structure_image_b64 ?? null }], mode: 'id' });
          const vSynonyms: string[] = Array.from(new Set(
            [data.result.label, ...(data.result.equivalent_identifiers ?? []).map((eq: EqIdentifier) => eq.label)]
              .filter((l: string | null): l is string => !!l)
          ));
          onChange({ ...value, vehicle_type: option.value, chemical_id: data.result.primary_id ?? '', unrecognized_chemical_name: '', synonym: vSynonyms });
        } else {
          setNorm({ status: 'error', message: 'No cached data for this vehicle.' });
        }
      })
      .catch(() => { if (!cancelled) setNorm({ status: 'error', message: 'Network error.' }); });
    return () => { cancelled = true; };
  }, [value.vehicle_type, mode]);

  const normFetch = async (body: object, queriedId: string): Promise<NormResultItem | null> => {
    try {
      const res = await fetch('/api/chemicals/normalize', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await res.json();
      if (!res.ok) return null;
      return { queried_id: queriedId, result: data.result as NormResult, imageB64: data.structure_image_b64 ?? null };
    } catch { return null; }
  };

  const normFetchAll = async (body: object): Promise<NormResultItem[]> => {
    try {
      const res = await fetch('/api/chemicals/normalize', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await res.json();
      if (!res.ok) return [];
      const list: NormResult[] = Array.isArray(data.results) && data.results.length > 0
        ? data.results : data.result?.normalized ? [data.result] : [];
      return list.filter((r) => r.normalized).map((r, i) => ({
        queried_id: r.primary_id ?? String(i),
        result: r,
        imageB64: i === 0 ? (data.structure_image_b64 ?? null) : null,
      }));
    } catch { return []; }
  };

  const lookupByName = async (name: string, knownChebiIds?: string[]): Promise<NormResultItem[]> => {
    let chebiIds = knownChebiIds;
    if (!chebiIds) {
      try {
        const res = await fetch(`/api/chemicals/autocomplete?q=${encodeURIComponent(name)}&limit=${acLimit}`);
        const suggestions: AcSuggestion[] = await res.json();
        chebiIds = suggestions.find((s) => s.name.toLowerCase() === name.toLowerCase())?.chebi_ids ?? [];
      } catch { chebiIds = []; }
    }
    const [chebiResults, nameResults] = await Promise.all([
      Promise.all(chebiIds.map((id) => normFetch({ namespace: 'CHEBI', chemical_id: id.replace('CHEBI:', '') }, id)))
        .then((rs) => rs.filter((r): r is NormResultItem => r !== null && r.result.normalized)),
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
    setNorm({ status: 'loading' });
    const items = await lookupByName(suggestion.name, suggestion.chebi_ids);
    setNorm(items.length > 0 ? { status: 'done', items, mode: 'name' } : { status: 'error', message: 'No results found.' });
  };

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
      const synonyms = Array.from(new Set(
        [item.result.label, ...item.result.equivalent_identifiers.map((eq) => eq.label)]
          .filter((l): l is string => !!l)
      ));
      onChange({ ...value, chemical_id: item.result.primary_id, synonym: synonyms });
      setInfoRevealed(true);
    }
  };

  // Manufacturer "other" logic
  const knownMfrs = MANUFACTURER_OPTIONS.filter((o) => o.value !== '' && o.value !== '__other__').map((o) => o.value);
  const isOtherMfr = !!value.manufacturer && !knownMfrs.includes(value.manufacturer);
  const mfrSelectVal = isOtherMfr ? '__other__' : (value.manufacturer || '');
  const showMfrFreeText = otherMfrPending || isOtherMfr;

  // Vehicle "other" logic — options without a meaning CURIE need a free-text field
  const selectedVehicleOption = mode === 'vehicle' ? VEHICLE_OPTIONS.find((o) => o.value === value.vehicle_type) : undefined;
  const vehicleHasNoMeaning = mode === 'vehicle' && !!value.vehicle_type && !selectedVehicleOption?.meaning;

  return (
    <div className="col-12" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

      {/* ── 1. Lookup bar ── */}
      <div style={LOOKUP_BAR}>
        <div style={SECTION_LABEL}>
          {mode === 'vehicle' ? 'Vehicle type' : 'Lookup substance name / ID'}
        </div>
        {mode === 'vehicle' ? (
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select
              aria-label="Vehicle type"
              value={value.vehicle_type || ''}
              onChange={(e) => applyChange({ vehicle_type: e.target.value })}
              style={{ ...BAR_SELECT, flex: 1 }}
            >
              {VEHICLE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            {norm.status === 'loading' && (
              <span style={{ fontSize: '0.82rem', color: '#888', flexShrink: 0 }}>Looking up…</span>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <select
              aria-label="ID Type"
              value={idTypeValue}
              onChange={(e) => applyChange({ idType: e.target.value as SubstanceIdType })}
              style={{ ...BAR_SELECT, flex: '0 0 auto', minWidth: '140px' }}
            >
              {SUBSTANCE_IDTYPE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            <div style={{ flex: 1, position: 'relative' }}>
              <input
                type="text"
                aria-label={useNameResolver ? 'Chemical name' : 'Chemical identifier'}
                placeholder={useNameResolver ? 'Chemical name, e.g. ethanol' : 'Identifier, e.g. 16236'}
                value={value.id || ''}
                onChange={(e) => applyChange({ id: e.target.value })}
                onBlur={() => setTimeout(() => setAc({ status: 'idle' }), 150)}
                style={BAR_INPUT}
              />
              {ac.status === 'open' && (
                <ul style={{
                  position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                  margin: 0, padding: 0, listStyle: 'none',
                  border: '1px solid #ccc', borderRadius: '4px',
                  background: '#fff', boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
                  maxHeight: '220px', overflowY: 'auto',
                }}>
                  {ac.suggestions.map((s) => (
                    <li
                      key={s.name}
                      onMouseDown={() => handleSuggestionClick(s)}
                      style={{
                        padding: '7px 10px', cursor: 'pointer', fontSize: '0.85rem',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
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
              style={{ height: '34px', padding: '0 14px', fontSize: '0.88rem', whiteSpace: 'nowrap', flexShrink: 0 }}
            >
              {norm.status === 'loading' ? 'Looking up…' : 'Find chemical ↗'}
            </button>
          </div>
        )}
      </div>

      {/* ── 2. Results (fixed height for substance, card-height for vehicle) ── */}
      <div style={SECTION_BOX}>
        <div style={{ ...SECTION_LABEL, marginBottom: '8px' }}>
          {mode === 'vehicle'
            ? 'Vehicle information'
            : norm.status === 'done'
              ? `Suggested result${norm.items.length > 1 ? `s (${norm.items.length})` : ''}`
              : 'Suggested results'}
        </div>
        <div style={{
          ...(mode !== 'vehicle' ? { height: `${RESULTS_HEIGHT}px` } : { minHeight: `${CARD_HEIGHT}px` }),
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          paddingRight: '2px',
        }}>
          {norm.status === 'idle' && (
            <div style={{
              height: '100%',
              minHeight: mode === 'vehicle' ? `${CARD_HEIGHT}px` : undefined,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#bbb', fontSize: '0.85rem', fontStyle: 'italic', userSelect: 'none',
            }}>
              {mode === 'vehicle' ? 'Select a vehicle type above' : 'Enter a name or ID above and click Find chemical'}
            </div>
          )}
          {norm.status === 'loading' && (
            <div style={{
              height: '100%',
              minHeight: mode === 'vehicle' ? `${CARD_HEIGHT}px` : undefined,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#888', fontSize: '0.88rem',
            }}>
              Looking up…
            </div>
          )}
          {norm.status === 'error' && (
            <div style={{ color: '#c00', fontSize: '0.82rem', padding: '4px 2px' }}>{norm.message}</div>
          )}
          {norm.status === 'done' && norm.items.map((item, idx) =>
            item.result.normalized ? (
              <ResultCard key={idx} item={item} onAccept={() => handleAccept(item)} hideAccept={mode === 'vehicle'} />
            ) : (
              <div key={idx} style={{ color: '#888', fontSize: '0.82rem' }}>No match for {item.queried_id}</div>
            )
          )}
        </div>
      </div>

      {/* ── 3. Standardized info (2-column grid, only in substance mode) ── */}
      {mode === 'substance' && (
        <div style={SECTION_BOX}>
          <div style={SECTION_LABEL}>Standardized information</div>
          {!infoRevealed ? (
            /* Placeholder — mirrors the idle suggested-results state */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '10px', padding: '18px 0' }}>
              <div style={{ color: '#bbb', fontSize: '0.85rem', fontStyle: 'italic', textAlign: 'center' }}>
                Search for a substance above and click <strong style={{ fontStyle: 'normal', color: '#999' }}>Use</strong> to auto-populate standardized information
              </div>
              <button
                type="button"
                onClick={() => setInfoRevealed(true)}
                style={{ fontSize: '0.78rem', padding: '3px 14px', color: '#5a7a5a', border: '1px solid #aac8aa', borderRadius: '4px', background: '#f4f9f4', cursor: 'pointer' }}
              >
                Standardized ID unavailable / unrecognized
              </button>
            </div>
          ) : (
            /* Full form */
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 20px' }}>
              {/* Left column: Standardized ID, Unavailable/unrecognized, CAS */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <Input
                  label="Standardized ID"
                  placeholder="Accepted standardized identifier"
                  tooltip={EXPOSURE_SUBSTANCE}
                  value={value.chemical_id || ''}
                  disabled
                  onChange={(e) => applyChange({ chemical_id: e.target.value })}
                  labelAction={!!value.chemical_id && (
                    <button
                      type="button"
                      onClick={() => applyChange({ chemical_id: undefined, synonym: undefined })}
                      style={{ fontSize: '0.72rem', color: '#999', background: 'none', border: 'none', padding: 0, cursor: 'pointer', textDecoration: 'underline' }}
                    >
                      × Clear selection
                    </button>
                  )}
                />
                <Input
                  label="Unavailable / unrecognized substance or ID"
                  placeholder="Enter free text if no standardized ID is available"
                  value={value.unrecognized_chemical_name || ''}
                  disabled={!!value.chemical_id}
                  onChange={(e) => applyChange({ unrecognized_chemical_name: e.target.value })}
                />
                <Input
                  label="CAS Number"
                  placeholder="e.g. 64-17-5"
                  value={value.cas_id || ''}
                  onChange={(e) => applyChange({ cas_id: e.target.value })}
                />
              </div>

              {/* Right column: Manufacturer, Concentration + unit, Comment */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                  <div className="field" style={{ flex: showMfrFreeText ? '0 0 auto' : '1' }}>
                    <div className="inline"><label>Manufacturer</label></div>
                    <select
                      value={otherMfrPending ? '__other__' : mfrSelectVal}
                      onChange={(e) => {
                        const v = e.target.value;
                        if (v === '__other__') { setOtherMfrPending(true); }
                        else { setOtherMfrPending(false); applyChange({ manufacturer: v }); }
                      }}
                    >
                      {MANUFACTURER_OPTIONS.map((o) => (
                        <option key={o.value} value={o.value}>{o.label}</option>
                      ))}
                    </select>
                  </div>
                  {showMfrFreeText && (
                    <div className="field" style={{ flex: 1 }}>
                      <div className="inline"><label>Manufacturer unlisted</label></div>
                      <input
                        type="text"
                        placeholder="Enter manufacturer name"
                        value={value.manufacturer || ''}
                        onChange={(e) => { setOtherMfrPending(false); applyChange({ manufacturer: e.target.value }); }}
                      />
                    </div>
                  )}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px', gap: '8px' }}>
                  <Input
                    label="Concentration"
                    placeholder="e.g. 10"
                    type="number"
                    value={value.concentration ?? ''}
                    onChange={(e) => applyChange({ concentration: e.target.value === '' ? null : Number(e.target.value) })}
                  />
                  <Select
                    label="Unit"
                    value={value.concentration_unit || ''}
                    options={[{ value: '', label: '—' }, ...CONC_UNIT_OPTIONS]}
                    onChange={(e) => applyChange({ concentration_unit: (e.target as HTMLSelectElement).value })}
                  />
                </div>
                <Input
                  label="Comment"
                  placeholder="Optional note about this substance"
                  value={value.comment || ''}
                  onChange={(e) => applyChange({ comment: e.target.value })}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Vehicle mode: identical 2-column grid to substance, gated on vehicle selection */}
      {mode === 'vehicle' && (
        <div style={SECTION_BOX}>
          <div style={SECTION_LABEL}>Standardized information</div>
          {!value.vehicle_type ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '18px 0', color: '#bbb', fontSize: '0.85rem', fontStyle: 'italic', textAlign: 'center' }}>
              Select a vehicle type above to populate standardized information
            </div>
          ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 20px' }}>
            {/* Left column: vehicle identity */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
              <Input
                label="Standardized ID"
                placeholder="Accepted standardized identifier"
                tooltip={EXPOSURE_SUBSTANCE}
                value={value.chemical_id || ''}
                disabled={!!value.chemical_id || vehicleHasNoMeaning}
                onChange={(e) => applyChange({ chemical_id: e.target.value })}
              />
              <Input
                label="Unlisted vehicle name"
                placeholder="Enter vehicle name if not listed"
                value={value.unrecognized_chemical_name || ''}
                disabled={!vehicleHasNoMeaning}
                onChange={(e) => applyChange({ unrecognized_chemical_name: e.target.value })}
              />
              <Input
                label="CAS Number"
                placeholder="e.g. 64-17-5"
                value={value.cas_id || ''}
                onChange={(e) => applyChange({ cas_id: e.target.value })}
              />
            </div>

            {/* Right column: identical to substance */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                <div className="field" style={{ flex: showMfrFreeText ? '0 0 auto' : '1' }}>
                  <div className="inline"><label>Manufacturer</label></div>
                  <select
                    value={otherMfrPending ? '__other__' : mfrSelectVal}
                    onChange={(e) => {
                      const v = e.target.value;
                      if (v === '__other__') { setOtherMfrPending(true); }
                      else { setOtherMfrPending(false); applyChange({ manufacturer: v }); }
                    }}
                  >
                    {MANUFACTURER_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
                {showMfrFreeText && (
                  <div className="field" style={{ flex: 1 }}>
                    <div className="inline"><label>Manufacturer unlisted</label></div>
                    <input
                      type="text"
                      placeholder="Enter manufacturer name"
                      value={value.manufacturer || ''}
                      onChange={(e) => { setOtherMfrPending(false); applyChange({ manufacturer: e.target.value }); }}
                    />
                  </div>
                )}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px', gap: '8px' }}>
                <Input
                  label="Concentration"
                  placeholder="e.g. 10"
                  type="number"
                  value={value.concentration ?? ''}
                  onChange={(e) => applyChange({ concentration: e.target.value === '' ? null : Number(e.target.value) })}
                />
                <Select
                  label="Unit"
                  value={value.concentration_unit || ''}
                  options={[{ value: '', label: '—' }, ...CONC_UNIT_OPTIONS]}
                  onChange={(e) => applyChange({ concentration_unit: (e.target as HTMLSelectElement).value })}
                />
              </div>
              <Input
                label="Comment"
                placeholder="Optional note about this vehicle"
                value={value.comment || ''}
                onChange={(e) => applyChange({ comment: e.target.value })}
              />
            </div>
          </div>
          )}
        </div>
      )}

    </div>
  );
}
