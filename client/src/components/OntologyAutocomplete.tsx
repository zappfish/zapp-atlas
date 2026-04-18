import React, { useEffect, useRef, useState } from 'react';

import type { OntologyHit } from '@/api/exposures';

interface Props {
  value: { term_uri: string; term_label?: string | null } | null;
  onChange: (hit: OntologyHit | null) => void;
  search: (q: string) => Promise<OntologyHit[]>;
  placeholder?: string;
  ariaLabel: string;
}

export default function OntologyAutocomplete({
  value,
  onChange,
  search,
  placeholder,
  ariaLabel,
}: Props) {
  const [query, setQuery] = useState('');
  const [hits, setHits] = useState<OntologyHit[]>([]);
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
      search(query)
        .then((rows) => !cancelled && setHits(rows))
        .catch(() => !cancelled && setHits([]))
        .finally(() => !cancelled && setLoading(false));
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [query, open, search]);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (!boxRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  function pick(hit: OntologyHit) {
    onChange(hit);
    setQuery('');
    setOpen(false);
  }

  return (
    <div className="autocomplete" ref={boxRef}>
      {value ? (
        <div className="selected-fish">
          <strong>{value.term_label || '—'}</strong>
          <span className="muted"> ({value.term_uri})</span>
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
            placeholder={placeholder}
            aria-label={ariaLabel}
          />
          {open && (query.trim().length >= 2 || loading) && (
            <ul className="autocomplete-menu" role="listbox">
              {loading && <li className="muted">Searching…</li>}
              {!loading && hits.length === 0 && <li className="muted">No matches.</li>}
              {!loading &&
                hits.map((h) => (
                  <li key={h.term_uri}>
                    <button type="button" onClick={() => pick(h)}>
                      <strong>{h.term_label}</strong>
                      <span className="muted"> ({h.term_uri})</span>
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
