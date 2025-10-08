import React from 'react';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import TextArea from '@/ui/TextArea';
import type { ZappObservation } from '@/schema';
import { WT_OPTIONS } from './constants';
import { FISH_STRAIN } from './explanations';

export default function FishInfoSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  const [showNotes, setShowNotes] = React.useState(false);
  return (
    <div className="row">
      <FormSection title="Fish Information">
        <div className="col-6">
          <Select
            label="Strain/Background (WT)"
            value={data.fish.strain_background || ''}
            options={WT_OPTIONS}
            tooltip={FISH_STRAIN}
            onChange={(e) =>
              update((d) => ({
                ...d,
                fish: {
                  ...d.fish,
                  strain_background: (e.target as HTMLSelectElement).value
                }
              }))
            }
          />
        </div>
        <div className="col-6">
          <div className="field">
            <label>Transgene/Line, Mutant line</label>
            <small className="hint">Autocomplete from ZFIN — TODO in later iteration.</small>
          </div>
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
