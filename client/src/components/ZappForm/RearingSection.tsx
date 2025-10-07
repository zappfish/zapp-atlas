import React from 'react';
import TextArea from '@/ui/TextArea';
import FormSection from '@/ui/FormSection';
import Tooltip from '@/ui/Tooltip';
import type { ZappObservation } from '@/schema';
import { REARING_STANDARD, REARING_NONSTANDARD } from './explanations';

export default function RearingSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  return (
    <div className="row">
      <FormSection title="Fish Rearing Conditions">
        <div className="col-4">
          <div className="field">
            <div className="inline">
              <label>Standard rearing (Westerfield 2000)</label>
              <Tooltip text={REARING_STANDARD} />
            </div>
            <div className="inline">
              <input
                type="checkbox"
                checked={data.rearing.standard}
                onChange={(e) => {
                  const checked = e.target.checked;
                  update((d) => ({
                    ...d,
                    rearing: {
                      ...d.rearing,
                      standard: checked,
                      non_standard_notes: checked ? '' : d.rearing.non_standard_notes
                    }
                  }));
                }}
              />
              <span>{data.rearing.standard ? 'Standard' : 'Not standard'}</span>
            </div>
          </div>
        </div>
        {!data.rearing.standard && (
          <div className="col-8">
            <TextArea
              label="If not standard, list differences"
              placeholder="List parameters that do not follow standard (temperature, light/dark, pH, water type, density, etc.)"
              tooltip={REARING_NONSTANDARD}
              value={data.rearing.non_standard_notes || ''}
              onChange={(e) =>
                update((d) => ({
                  ...d,
                  rearing: { ...d.rearing, non_standard_notes: e.target.value }
                }))
              }
            />
          </div>
        )}
      </FormSection>
    </div>
  );
}
