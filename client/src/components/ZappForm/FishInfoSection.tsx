import React from 'react';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import type { ZappObservation } from '@/schema';
import { WT_OPTIONS } from './constants';

export default function FishInfoSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  return (
    <div className="row">
      <FormSection title="Fish Information">
        <div className="col-6">
          <Select
            label="Strain/Background (WT)"
            value={data.fish.strain_background || ''}
            options={WT_OPTIONS}
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
      </FormSection>
    </div>
  );
}
