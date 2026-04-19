import React, { useEffect, useRef, useState } from 'react';

import { fishAutocomplete, type ZfinHit } from '@/api/experiments';
import ZfinLabel from '@/components/ZfinLabel';
import type { Fish } from '@/types';

interface Props {
  value: Fish | null;
  onChange: (fish: Fish | null) => void;
}

export default function FishAutocomplete({ value, onChange }: Props) {
  const [query, setQuery] = useState('');
  const [hits, setHits] = useState<ZfinHit[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open || query.trim().length < 2) {
      setHits([]);
      return;
    }
    let cancelled = false;
    setLoading(true);
    const t = setTimeout(() => {
      fishAutocomplete(query)
        .then((rows) => {
          if (!cancelled) setHits(rows);
        })
        .catch(() => {
          if (!cancelled) setHits([]);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 200);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [query, open]);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (!boxRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  function pick(hit: ZfinHit) {
    onChange({
      zfin_id: hit.id.startsWith('ZFIN:') ? hit.id : `ZFIN:${hit.id}`,
      name: hit.name,
    });
    setQuery('');
    setOpen(false);
  }

  return (
    <div className="autocomplete" ref={boxRef}>
      {value ? (
        <div className="selected-fish">
          <ZfinLabel text={value.name} className="fish-label" />
          <span className="muted"> ({value.zfin_id})</span>
          <button type="button" className="link-button" onClick={() => onChange(null)}>
            change
          </button>
        </div>
      ) : (
        <>
          <input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            placeholder="Type fish name (e.g. AB, TU)…"
            aria-label="Fish autocomplete"
          />
          {open && (query.trim().length >= 2 || loading) && (
            <ul className="autocomplete-menu" role="listbox">
              {loading && <li className="muted">Searching…</li>}
              {!loading && hits.length === 0 && <li className="muted">No matches.</li>}
              {!loading &&
                hits.map((h) => (
                  <li key={h.id}>
                    <button type="button" onClick={() => pick(h)}>
                      <ZfinLabel text={h.name} className="fish-label" />
                      <span className="muted"> ({h.id})</span>
                    </button>
                  </li>
                ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
