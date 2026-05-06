import React from 'react';
import Input from '@/ui/Input';
import FormSection from '@/ui/FormSection';
import TextArea from '@/ui/TextArea';
import type { ZappObservation } from '@/schema';
import { wildTypeLines, defaultWildTypeSuggestions } from '@/data/wildTypeLines';
import { FISH_STRAIN } from './explanations';

export default function FishInfoSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  const [showNotes, setShowNotes] = React.useState(false);
  const [query, setQuery] = React.useState<string>(data.fish.strain_background || '');
  const [isOpen, setIsOpen] = React.useState(false);
  const [highlight, setHighlight] = React.useState(0);
  const containerRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if ((data.fish.strain_background || '') !== query) {
      setQuery(data.fish.strain_background || '');
    }
  }, [data.fish.strain_background]);

  const norm = (s: string) => s.toLowerCase();

  const suggestions = React.useMemo(() => {
    const q = query.trim();
    if (!q) return defaultWildTypeSuggestions;
    const qn = norm(q);
    return wildTypeLines
      .filter((w) => norm(w.code).includes(qn) || norm(w.genoId).includes(qn) || norm(w.fishId).includes(qn))
      .slice(0, 20);
  }, [query]);

  React.useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(e.target as Node)) setIsOpen(false);
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const onSelect = (w: { code: string; genoId: string; fishId: string }) => {
    setQuery(w.code);
    update((d) => ({ ...d, fish: { ...d.fish, strain_background: w.code } }));
    setIsOpen(false);
  };

  const onCommitFreeText = () => {
    update((d) => ({ ...d, fish: { ...d.fish, strain_background: query } }));
    setIsOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
      setIsOpen(true);
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (suggestions.length > 0) setHighlight((h) => Math.min(h + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (suggestions.length > 0) setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === 'Enter') {
      if (isOpen && suggestions.length > 0) {
        e.preventDefault();
        const i = Math.min(highlight, suggestions.length - 1);
        const choice = suggestions[i];
        if (choice) onSelect(choice);
      } else {
        onCommitFreeText();
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };
  return (
    <div className="row">
      <FormSection title="Fish Information">
        <div className="col-6">
          <div ref={containerRef} style={{ position: 'relative' }}>
            <Input
              label="Strain/Background (WT)"
              placeholder="Type a line code (e.g., AB, TL, TU, WIK)…"
              value={query}
              tooltip={FISH_STRAIN}
              onChange={(e) => {
                setQuery(e.target.value);
                update((d) => ({ ...d, fish: { ...d.fish, strain_background: e.target.value } }));
                if (e.target.value.trim()) setIsOpen(true);
              }}
              onFocus={() => {
                setIsOpen(true);
              }}
              onKeyDown={handleKeyDown}
            />
            {isOpen && (
              <div
                role="listbox"
                aria-label="Wild-type lines"
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
                {suggestions.map((w, i) => {
                  const active = i === highlight;
                  return (
                    <div
                      key={w.code}
                      role="option"
                      aria-selected={active}
                      onMouseDown={(e) => {
                        e.preventDefault();
                        onSelect(w);
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
                      <div style={{ fontWeight: 500 }}>{w.code}</div>
                      <div
                        style={{
                          fontSize: 12,
                          color: '#333',
                          background: '#f4f4f4',
                          border: '1px solid #e5e5e5',
                          borderRadius: 3,
                          padding: '2px 6px',
                          whiteSpace: 'nowrap'
                        }}
                        title="ZFIN identifiers"
                      >
                        {w.genoId} • {w.fishId}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
        <div className="col-6">
          <TextArea
            label="Line description"
            placeholder="If you don't see your wild type, or you have a transgenic or mutant line, enter its description here."
            value={data.fish.description || ''}
            onChange={(e) =>
              update((d) => ({
                ...d,
                fish: { ...d.fish, description: (e.target as HTMLTextAreaElement).value }
              }))
            }
          />
        </div>
        <div className="col-12">
          <button type="button" onClick={() => setShowNotes((s) => !s)}>
            {showNotes ? 'Hide notes' : 'Add notes'}
          </button>
        </div>
        {showNotes && (
          <div className="col-12">
            <TextArea
              label="Additional notes"
              placeholder="Additional notes not captured by the fields in this section"
              value={data.fish.additional_notes || ''}
              onChange={(e) =>
                update((d) => ({
                  ...d,
                  fish: { ...d.fish, additional_notes: (e.target as HTMLTextAreaElement).value }
                }))
              }
            />
          </div>
        )}
      </FormSection>
    </div>
  );
}
