import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import type { ZappObservation } from '@/schema';
import { STAGE_UNIT_OPTIONS, SEVERITY_OPTIONS } from './constants';
import {
  PHENOTYPE_OBS_STAGE_VALUE,
  PHENOTYPE_OBS_STAGE_UNIT,
  PHENOTYPE_TERM,
  PHENOTYPE_PREVALENCE,
  PHENOTYPE_SEVERITY
} from './explanations';

type StageUnit = 'hpf' | 'dpf' | 'month';
type Severity = 'mild' | 'moderate' | 'severe';

type Props = {
  data: ZappObservation;
  update: (u: (d: ZappObservation) => ZappObservation) => void;
  addPhenotype: () => void;
  removePhenotype: (idx: number) => void;
};

export default function PhenotypeSection({ data, update, addPhenotype, removePhenotype }: Props) {
  return (
    <div className="row">
      <FormSection title="Fish Phenotype">
        <div className="col-3">
          <Input
            label="Observation stage value"
            type="number"
            tooltip={PHENOTYPE_OBS_STAGE_VALUE}
            value={data.phenotype.observation_stage.value ?? ''}
            onChange={(e) =>
              update((d) => ({
                ...d,
                phenotype: {
                  ...d.phenotype,
                  observation_stage: {
                    ...d.phenotype.observation_stage,
                    value: e.target.value === '' ? null : Number(e.target.value)
                  }
                }
              }))
            }
          />
        </div>
        <div className="col-3">
          <Select
            label="Observation stage unit"
            value={data.phenotype.observation_stage.unit || ''}
            options={STAGE_UNIT_OPTIONS}
            tooltip={PHENOTYPE_OBS_STAGE_UNIT}
            onChange={(e) =>
              update((d) => ({
                ...d,
                phenotype: {
                  ...d.phenotype,
                  observation_stage: {
                    ...d.phenotype.observation_stage,
                    unit: (e.target as HTMLSelectElement).value as StageUnit
                  }
                }
              }))
            }
          />
        </div>

        {data.phenotype.items.map((item, idx) => (
          <React.Fragment key={idx}>
            <div className="col-8">
              <Input
                label={`Observed phenotype ${idx + 1} (ontology term — TODO)`}
                placeholder="Ontology term picker will be added"
                tooltip={PHENOTYPE_TERM}
                value={item.termLabel || ''}
                onChange={(e) =>
                  update((d) => ({
                    ...d,
                    phenotype: {
                      ...d.phenotype,
                      items: d.phenotype.items.map((it, i) =>
                        i === idx ? { ...it, termLabel: e.target.value } : it
                      )
                    }
                  }))
                }
              />
            </div>
            <div className="col-2">
              <Input
                label="Prevalence (%)"
                type="number"
                tooltip={PHENOTYPE_PREVALENCE}
                value={item.prevalencePercent ?? ''}
                onChange={(e) =>
                  update((d) => ({
                    ...d,
                    phenotype: {
                      ...d.phenotype,
                      items: d.phenotype.items.map((it, i) =>
                        i === idx
                          ? { ...it, prevalencePercent: e.target.value === '' ? null : Number(e.target.value) }
                          : it
                      )
                    }
                  }))
                }
              />
            </div>
            <div className="col-2">
              <Select
                label="Severity"
                value={item.severity || ''}
                options={SEVERITY_OPTIONS}
                tooltip={PHENOTYPE_SEVERITY}
                onChange={(e) =>
                  update((d) => ({
                    ...d,
                    phenotype: {
                      ...d.phenotype,
                      items: d.phenotype.items.map((it, i) =>
                        i === idx ? { ...it, severity: ((e.target as HTMLSelectElement).value || null) as Severity | null } : it
                      )
                    }
                  }))
                }
              />
            </div>
            <div className="row" style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button type="button" onClick={() => removePhenotype(idx)}>
                Remove phenotype
              </button>
            </div>
          </React.Fragment>
        ))}
        <div className="row">
          <button type="button" onClick={addPhenotype}>+ Add phenotype</button>
        </div>
      </FormSection>
    </div>
  );
}
