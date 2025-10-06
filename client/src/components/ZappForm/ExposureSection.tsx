import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import type { ZappObservation } from '@/schema';
import { CONC_UNIT_OPTIONS, PATTERN_OPTIONS, STAGE_UNIT_OPTIONS } from './constants';
import SubstanceFields from './SubstanceFields';

type ExposureRoute = 'water' | 'injected' | 'ingested';
type ExposureType = 'continuous' | 'repeated';
type ExposurePattern = 'static' | 'static_renewal' | 'flow_through';
type ConcUnit = 'uM' | 'mg/L';
type StageUnit = 'hpf' | 'dpf' | 'month';

export default function ExposureSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  const route = data.exposure.route;
  const type = data.exposure.type;

  return (
    <div className="row">
      <FormSection title="Exposure Event">
        <SubstanceFields
          value={data.exposure.substance}
          onChange={(substance) =>
            update((d) => ({
              ...d,
              exposure: { ...d.exposure, substance }
            }))
          }
        />

        <div className="col-4">
          <Input
            label="Substance concentration"
            type="number"
            placeholder="e.g., 10"
            value={data.exposure.concentration.value ?? ''}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  concentration: {
                    ...d.exposure.concentration,
                    value: e.target.value === '' ? null : Number(e.target.value)
                  }
                }
              }))
            }
          />
        </div>
        <div className="col-2">
          <Select
            label="Unit"
            value={data.exposure.concentration.unit || ''}
            options={CONC_UNIT_OPTIONS}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  concentration: {
                    ...d.exposure.concentration,
                    unit: (e.target as HTMLSelectElement).value as ConcUnit
                  }
                }
              }))
            }
          />
        </div>
        <div className="col-6" />

        <div className="col-12">
          <div className="field">
            <label>Exposure route</label>
            <div className="inline" role="radiogroup" aria-label="Exposure route">
              {[
                { value: 'water', label: 'Added to water' },
                { value: 'injected', label: 'Injected' },
                { value: 'ingested', label: 'Ingested (diet)' }
              ].map((opt) => (
                <label key={opt.value} className="inline" style={{ gap: 4 }}>
                  <input
                    type="radio"
                    name="exposure-route"
                    value={opt.value}
                    checked={data.exposure.route === (opt.value as ExposureRoute)}
                    onChange={(e) => {
                      const routeVal = e.currentTarget.value as ExposureRoute;
                      update((d) => ({
                        ...d,
                        exposure: {
                          ...d.exposure,
                          route: routeVal,
                          type: routeVal === 'water' ? null : 'repeated',
                          pattern: null,
                          repeated: {
                            duration_per_exposure_hours: null,
                            frequency_count: null,
                            interval_hours: null
                          }
                        }
                      }));
                    }}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>
        </div>

        {route === 'water' && (
          <>
            <div className="col-12">
              <div className="field">
                  <label>Exposure type</label>
                  <div className="inline" role="radiogroup" aria-label="Exposure type">
                    {[
                      { value: 'continuous', label: 'Continuous exposure' },
                      { value: 'repeated', label: 'Repeated exposures' }
                    ].map((opt) => (
                      <label key={opt.value} className="inline" style={{ gap: 4 }}>
                        <input
                          type="radio"
                          name="exposure-type"
                          value={opt.value}
                          checked={data.exposure.type === (opt.value as ExposureType)}
                          onChange={(e) =>
                            update((d) => ({
                              ...d,
                              exposure: {
                                ...d.exposure,
                                type: e.currentTarget.value as ExposureType,
                                pattern: null,
                                repeated: {
                                  duration_per_exposure_hours: null,
                                  frequency_count: null,
                                  interval_hours: null
                                }
                              }
                            }))
                          }
                        />
                        {opt.label}
                      </label>
                    ))}
                  </div>
                </div>
            </div>

            {type === 'continuous' && (
              <div className="col-12">
                <div className="field">
                  <label>Exposure pattern</label>
                  <div className="inline" role="radiogroup" aria-label="Exposure pattern">
                    {PATTERN_OPTIONS.map((opt) => (
                      <label key={opt.value} className="inline" style={{ gap: 4 }}>
                        <input
                          type="radio"
                          name="exposure-pattern"
                          value={opt.value}
                          checked={data.exposure.pattern === (opt.value as ExposurePattern)}
                          onChange={(e) =>
                            update((d) => ({
                              ...d,
                              exposure: {
                                ...d.exposure,
                                pattern: e.currentTarget.value as ExposurePattern
                              }
                            }))
                          }
                        />
                        {opt.label}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
            {type === 'repeated' && (
              <>
                <div className="col-4">
                  <Input
                    label="Duration per exposure (hours)"
                    type="number"
                    value={data.exposure.repeated.duration_per_exposure_hours ?? ''}
                    onChange={(e) =>
                      update((d) => ({
                        ...d,
                        exposure: {
                          ...d.exposure,
                          repeated: {
                            ...d.exposure.repeated,
                            duration_per_exposure_hours: e.target.value === '' ? null : Number(e.target.value)
                          }
                        }
                      }))
                    }
                  />
                </div>
                <div className="col-4">
                  <Input
                    label="Exposure frequency (count)"
                    type="number"
                    value={data.exposure.repeated.frequency_count ?? ''}
                    onChange={(e) =>
                      update((d) => ({
                        ...d,
                        exposure: {
                          ...d.exposure,
                          repeated: {
                            ...d.exposure.repeated,
                            frequency_count: e.target.value === '' ? null : Number(e.target.value)
                          }
                        }
                      }))
                    }
                  />
                </div>
                <div className="col-4">
                  <Input
                    label="Interval between exposures (hours)"
                    type="number"
                    value={data.exposure.repeated.interval_hours ?? ''}
                    onChange={(e) =>
                      update((d) => ({
                        ...d,
                        exposure: {
                          ...d.exposure,
                          repeated: {
                            ...d.exposure.repeated,
                            interval_hours: e.target.value === '' ? null : Number(e.target.value)
                          }
                        }
                      }))
                    }
                  />
                </div>
              </>
            )}
          </>
        )}

        {route && route !== 'water' && (
          <>
            <div className="col-6">
              <Input
                label={route === 'injected' ? 'Injection frequency (count)' : 'Feeding with chemical (count)'}
                type="number"
                value={data.exposure.repeated.frequency_count ?? ''}
                onChange={(e) =>
                  update((d) => ({
                    ...d,
                    exposure: {
                      ...d.exposure,
                      repeated: {
                        ...d.exposure.repeated,
                        frequency_count: e.target.value === '' ? null : Number(e.target.value)
                      }
                    }
                  }))
                }
              />
            </div>
            <div className="col-6">
              <Input
                label={route === 'injected' ? 'Interval between injections (hours)' : 'Interval between feedings (hours)'}
                type="number"
                value={data.exposure.repeated.interval_hours ?? ''}
                onChange={(e) =>
                  update((d) => ({
                    ...d,
                    exposure: {
                      ...d.exposure,
                      repeated: {
                        ...d.exposure.repeated,
                        interval_hours: e.target.value === '' ? null : Number(e.target.value)
                      }
                    }
                  }))
                }
              />
            </div>
          </>
        )}

        <div className="col-12">
          <hr />
        </div>

        <div className="col-3">
          <Input
            label="Start stage value"
            type="number"
            value={data.exposure.start_stage.value ?? ''}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  start_stage: {
                    ...d.exposure.start_stage,
                    value: e.target.value === '' ? null : Number(e.target.value)
                  }
                }
              }))
            }
          />
        </div>
        <div className="col-3">
          <Select
            label="Start stage unit"
            value={data.exposure.start_stage.unit || ''}
            options={STAGE_UNIT_OPTIONS}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  start_stage: {
                    ...d.exposure.start_stage,
                    unit: (e.target as HTMLSelectElement).value as StageUnit
                  }
                }
              }))
            }
          />
        </div>
        <div className="col-3">
          <Input
            label="End stage value"
            type="number"
            value={data.exposure.end_stage.value ?? ''}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  end_stage: {
                    ...d.exposure.end_stage,
                    value: e.target.value === '' ? null : Number(e.target.value)
                  }
                }
              }))
            }
          />
        </div>
        <div className="col-3">
          <Select
            label="End stage unit"
            value={data.exposure.end_stage.unit || ''}
            options={STAGE_UNIT_OPTIONS}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  end_stage: {
                    ...d.exposure.end_stage,
                    unit: (e.target as HTMLSelectElement).value as StageUnit
                  }
                }
              }))
            }
          />
        </div>

        <div className="row">
          <div className="field">
            <label>Note</label>
            <small className="hint">Ontology stage picker (ZFS) is TODO. Numeric + unit captured here.</small>
          </div>
        </div>
      </FormSection>
    </div>
  );
}
