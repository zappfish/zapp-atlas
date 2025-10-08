import React, { useEffect, useMemo, useRef, useState } from 'react';
import Input from '@/ui/Input';
import { EXPOSURE_SUBSTANCE } from './explanations';

type Substance = {
  name?: string;
  idType: 'PubChem' | 'CAS' | 'ChEBI' | 'None';
  id?: string;
};

type SubstanceRecord = {
  label: string;
  cas_numbers: string[];
  chebi_ids: string[];
  pubchem_cids: string[];
  synonyms: string[];
};

type IndexedRecord = {
  rec: SubstanceRecord;
  // Precomputed searchable strings (normalized)
  searchStr: string;
  labelNorm: string;
  synonymNorms: string[];
  idNorms: string[]; // CAS/ChEBI/PubChem merged
};

const stripDiacritics = (s: string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
const norm = (s: string) => stripDiacritics(s).toLowerCase();

function buildIndex(records: SubstanceRecord[]): IndexedRecord[] {
  return records.map((rec) => {
    const labelNorm = norm(rec.label);
    const synonymNorms = (rec.synonyms || []).map(norm);
    const idNorms = [
      ...(rec.cas_numbers || []).map(norm),
      ...(rec.chebi_ids || []).map(norm),
      ...(rec.pubchem_cids || []).map(norm)
    ];
    const searchStr = [labelNorm, ...synonymNorms, ...idNorms].join(' ');
    return { rec, searchStr, labelNorm, synonymNorms, idNorms };
  });
}

function rankRecord(idx: IndexedRecord, q: string): number {
  // Lower is better
  if (idx.labelNorm.startsWith(q)) return 0;
  if (idx.labelNorm.includes(q)) return 1;
  if (idx.synonymNorms.some((s) => s.startsWith(q))) return 2;
  if (idx.synonymNorms.some((s) => s.includes(q))) return 3;
  if (idx.idNorms.some((s) => s.startsWith(q))) return 4;
  if (idx.idNorms.some((s) => s.includes(q))) return 5;
  return 99;
}

export default function SubstanceFields({
  value,
  onChange
}: {
  value: Substance;
  onChange: (next: Substance) => void;
}) {
  // Local UI state
  const [query, setQuery] = useState<string>(value.name || '');
  const [isOpen, setIsOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const [isLinked, setIsLinked] = useState<boolean>(false);
  const [records, setRecords] = useState<IndexedRecord[] | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Keep query in sync if external value changes
  useEffect(() => {
    if (value.name !== query) {
      setQuery(value.name || '');
    }
    // value.idType might be anything initially; we enforce CAS internally on any change
  }, [value.name]);

  // Lazy-load dataset on first focus (served from /public as /data/substances.sample.json)
  const ensureLoaded = async () => {
    if (records) return;
    try {
      const res = await fetch('/data/substances.sample.json', { cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const recs = (await res.json()) as SubstanceRecord[];
      setRecords(buildIndex(recs));
    } catch (e) {
      // If loading fails, keep records null; user can still free-text
      console.error('Failed to load substances dataset', e);
      setRecords([]);
    }
  };

  // Compute suggestions
  const suggestions = useMemo(() => {
    if (!records || !query.trim()) return [];
    const q = norm(query.trim());
    const withRank = records
      .map((r) => ({ r, rank: rankRecord(r, q) }))
      .filter((x) => x.rank < 99)
      .sort((a, b) => (a.rank - b.rank) || a.r.rec.label.localeCompare(b.r.rec.label))
      .slice(0, 20)
      .map((x) => x.r);
    return withRank;
  }, [records, query]);

  // Close on outside click
  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const applyChange = (partial: Partial<Substance>) => {
    onChange({
      ...value,
      idType: 'CAS',
      ...partial
    });
  };

  const onSelect = (rec: SubstanceRecord) => {
    const firstCAS = rec.cas_numbers?.[0] || '';
    setQuery(rec.label);
    applyChange({ name: rec.label, id: firstCAS, idType: 'CAS' });
    setIsLinked(true);
    setIsOpen(false);
  };

  const onCommitFreeText = () => {
    // When committing free text, do not auto-fill id
    applyChange({ name: query, idType: 'CAS' });
    setIsLinked(false);
    setIsOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
      setIsOpen(true);
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (suggestions.length > 0) {
        setHighlight((h) => Math.min(h + 1, suggestions.length - 1));
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (suggestions.length > 0) {
        setHighlight((h) => Math.max(h - 1, 0));
      }
    } else if (e.key === 'Enter') {
      if (suggestions.length > 0) {
        e.preventDefault();
        const i = Math.min(highlight, suggestions.length - 1);
        const choice = suggestions[i];
        if (choice) onSelect(choice.rec);
      } else {
        // No suggestions -> commit free text
        onCommitFreeText();
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <>
      <div className="col-8">
        <div ref={containerRef} style={{ position: 'relative' }}>
          <Input
            label="Substance"
            placeholder="Type a chemical name, synonym, or CAS…"
            tooltip={EXPOSURE_SUBSTANCE}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              applyChange({ name: e.target.value });
              setIsLinked(false);
              if (e.target.value.trim()) setIsOpen(true);
            }}
            onFocus={() => {
              void ensureLoaded();
              if (query.trim()) setIsOpen(true);
            }}
            onKeyDown={handleKeyDown}
          />
          {isOpen && (suggestions.length > 0 || query.trim()) && (
            <div
              role="listbox"
              aria-label="Substance suggestions"
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                background: '#fff',
                border: '1px solid #ccc',
                boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
                zIndex: 10,
                maxHeight: 240,
                overflowY: 'auto'
              }}
            >
              {suggestions.map((idx, i) => {
                const rec = idx.rec;
                const firstCAS = rec.cas_numbers?.[0] || '';
                const subSyn = rec.synonyms?.[0] || '';
                const active = i === highlight;
                return (
                  <div
                    key={rec.label + firstCAS}
                    role="option"
                    aria-selected={active}
                    onMouseDown={(e) => {
                      // Prevent blur before selection
                      e.preventDefault();
                      onSelect(rec);
                    }}
                    onMouseEnter={() => setHighlight(i)}
                    style={{
                      padding: '8px 10px',
                      cursor: 'pointer',
                      background: active ? '#eef3ff' : '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: 8
                    }}
                  >
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{rec.label}</div>
                      {subSyn && (
                        <div style={{ fontSize: 12, color: '#555', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {subSyn}
                        </div>
                      )}
                    </div>
                    {firstCAS && (
                      <div
                        style={{
                          fontSize: 12,
                          color: '#333',
                          background: '#f4f4f4',
                          border: '1px solid #e5e5e5',
                          borderRadius: 3,
                          padding: '2px 6px',
                          whiteSpace: 'nowrap',
                          marginLeft: 8
                        }}
                        title="CAS number"
                      >
                        CAS {firstCAS}
                      </div>
                    )}
                  </div>
                );
              })}
              {records && suggestions.length === 0 && query.trim() && (
                <div
                  onMouseDown={(e) => {
                    e.preventDefault();
                    onCommitFreeText();
                  }}
                  style={{
                    padding: '8px 10px',
                    cursor: 'pointer',
                    background: '#fff'
                  }}
                >
                  Use free text: “{query.trim()}”
                </div>
              )}
            </div>
          )}
          {!isLinked && query.trim() && (
            <div style={{ marginTop: 4, fontSize: 12, color: '#7a7a7a' }}>Free text (not linked to a controlled term)</div>
          )}
        </div>
      </div>
      <div className="col-4">
        <Input
          label="CAS number"
          placeholder="e.g., 50-00-0"
          value={value.id || ''}
          onChange={(e) => {
            applyChange({ id: e.target.value });
            setIsLinked(false);
          }}
        />
      </div>
    </>
  );
}
