import React, { useEffect, useState } from 'react';

import { wildtypeList } from '@/api/experiments';
import FishAutocomplete from '@/components/FishAutocomplete';
import type { Fish } from '@/types';

type Mode = 'wildtype' | 'strain';

interface Props {
  value: Fish | null;
  onChange: (fish: Fish | null) => void;
}

/**
 * Pick a fish as either a wild-type genetic background (curated list of
 * ZDB-GENO IDs that ZFIN's quicksearch does NOT surface) or a specific
 * strain (ZFIN fish autocomplete — transgenics, morphants, …).
 */
export default function FishPicker({ value, onChange }: Props) {
  const [wildtypes, setWildtypes] = useState<Fish[] | null>(null);
  const [mode, setMode] = useState<Mode>('wildtype');

  useEffect(() => {
    let cancelled = false;
    wildtypeList()
      .then((rows) => {
        if (cancelled) return;
        setWildtypes(rows.map((r) => ({ zfin_id: r.zfin_id, name: r.name })));
      })
      .catch(() => {
        if (!cancelled) setWildtypes([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // If editing and the current value is a known wild-type, open in wild-type
  // mode so the dropdown reflects the choice.
  useEffect(() => {
    if (value && wildtypes && wildtypes.some((w) => w.zfin_id === value.zfin_id)) {
      setMode('wildtype');
    }
  }, [value, wildtypes]);

  return (
    <div className="fish-picker">
      <div className="fish-picker-modes" role="radiogroup" aria-label="Fish source">
        <label className="inline-check">
          <input
            type="radio"
            name="fish-picker-mode"
            value="wildtype"
            checked={mode === 'wildtype'}
            onChange={() => setMode('wildtype')}
          />
          Wild-type background
        </label>
        <label className="inline-check">
          <input
            type="radio"
            name="fish-picker-mode"
            value="strain"
            checked={mode === 'strain'}
            onChange={() => setMode('strain')}
          />
          Specific strain (ZFIN search)
        </label>
      </div>

      {mode === 'wildtype' ? (
        <select
          aria-label="Wild-type genotype"
          value={value?.zfin_id ?? ''}
          onChange={(e) => {
            const wt = (wildtypes ?? []).find((w) => w.zfin_id === e.target.value);
            onChange(wt ?? null);
          }}
        >
          <option value="">— pick a wild-type —</option>
          {(wildtypes ?? []).map((w) => (
            <option key={w.zfin_id} value={w.zfin_id}>
              {w.name} ({w.zfin_id.replace('ZFIN:', '')})
            </option>
          ))}
        </select>
      ) : (
        <FishAutocomplete value={value} onChange={onChange} />
      )}
    </div>
  );
}
