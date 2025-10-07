import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import type { ZappObservation } from '@/schema';
import { CONC_UNIT_OPTIONS, PATTERN_OPTIONS, STAGE_UNIT_OPTIONS, DURATION_UNIT_OPTIONS } from './constants';
import SubstanceFields from './SubstanceFields';
import Tooltip from '@/ui/Tooltip';
import {
  EXPOSURE_CONCENTRATION_VALUE,
  EXPOSURE_CONCENTRATION_UNIT,
  EXPOSURE_ROUTE,
  EXPOSURE_REGIMEN,
  EXPOSURE_PATTERN,
  EXPOSURE_DURATION_VALUE,
  EXPOSURE_DURATION_UNIT,
  EXPOSURE_REP_DURATION_PER,
  EXPOSURE_REP_FREQUENCY,
  EXPOSURE_REP_INTERVAL,
  EXPOSURE_START_STAGE_VALUE,
  EXPOSURE_START_STAGE_UNIT,
  EXPOSURE_END_STAGE_VALUE,
  EXPOSURE_END_STAGE_UNIT
} from './explanations';

type ExposureRoute = 'water' | 'injected' | 'ingested' | 'gavage';
type ExposureType = 'continuous' | 'repeated';
type ExposurePattern = 'static' | 'static_renewal' | 'flow_through';
type ConcUnit = 'uM' | 'mg/L';
type StageUnit = 'hpf' | 'dpf' | 'month';
type DurationUnit = 'hour' | 'min';

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
            tooltip={EXPOSURE_CONCENTRATION_VALUE}
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
            tooltip={EXPOSURE_CONCENTRATION_UNIT}
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
            <div className="inline">
              <label>Exposure route</label>
              <Tooltip text={EXPOSURE_ROUTE} />
            </div>
            <div className="inline" role="radiogroup" aria-label="Exposure route">
              {[
                { value: 'water', label: 'via environment (ambient aquatic environment route)' },
                { value: 'ingested', label: 'via diet (ingestion)' },
                { value: 'gavage', label: 'via gavage' },
                { value: 'injected', label: 'via injection' }
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
                          duration: { value: null, unit: null },
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
                  <div className="inline">
                    <label>Exposure regimen</label>
                    <Tooltip text={EXPOSURE_REGIMEN} />
                  </div>
                  <div className="inline" role="radiogroup" aria-label="Exposure regimen">
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
                            update((d) => {
                              const nextType = e.currentTarget.value as ExposureType;
                              return ({
                                ...d,
                                exposure: {
                                  ...d.exposure,
                                  type: nextType,
                                  pattern: null,
                                  duration: nextType === 'continuous' ? d.exposure.duration : { value: null, unit: null },
                                  repeated: {
                                    duration_per_exposure_hours: null,
                                    frequency_count: null,
                                    interval_hours: null
                                  }
                                }
                              });
                            })
                          }
                        />
                        {opt.label}
                      </label>
                    ))}
                  </div>
                </div>
            </div>

            {type === 'continuous' && (
              <>
                <div className="col-4">
                  <Input
                    label="Exposure duration"
                    tooltip={EXPOSURE_DURATION_VALUE}
                    type="number"
                    value={data.exposure.duration.value ?? ''}
                    onChange={(e) =>
                      update((d) => ({
                        ...d,
                        exposure: {
                          ...d.exposure,
                          duration: {
                            ...d.exposure.duration,
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
                    tooltip={EXPOSURE_DURATION_UNIT}
                    value={data.exposure.duration.unit || ''}
                    options={DURATION_UNIT_OPTIONS}
                    onChange={(e) =>
                      update((d) => ({
                        ...d,
                        exposure: {
                          ...d.exposure,
                          duration: {
                            ...d.exposure.duration,
                            unit: (e.target as HTMLSelectElement).value as DurationUnit
                          }
                        }
                      }))
                    }
                  />
                </div>
                <div className="col-6" />
                <div className="col-12">
                  <div className="field">
                    <div className="inline">
                      <label>Exposure pattern</label>
                      <Tooltip text={EXPOSURE_PATTERN} />
                    </div>
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
              </>
            )}
            {type === 'repeated' && (
              <>
                <div className="col-4">
                  <Input
                    label="Duration per exposure (hours)"
                    type="number"
                    tooltip={EXPOSURE_REP_DURATION_PER}
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
                    tooltip={EXPOSURE_REP_FREQUENCY}
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
                    tooltip={EXPOSURE_REP_INTERVAL}
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
                label={
                  route === 'injected'
                    ? 'Injection frequency (count)'
                    : route === 'gavage'
                    ? 'Gavage frequency (count)'
                    : 'Feeding with chemical (count)'
                }
                type="number"
                tooltip={EXPOSURE_REP_FREQUENCY}
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
                label={
                  route === 'injected'
                    ? 'Interval between injections (hours)'
                    : route === 'gavage'
                    ? 'Interval between gavages (hours)'
                    : 'Interval between feedings (hours)'
                }
                type="number"
                tooltip={EXPOSURE_REP_INTERVAL}
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
            tooltip={EXPOSURE_START_STAGE_VALUE}
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
            tooltip={EXPOSURE_START_STAGE_UNIT}
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
            tooltip={EXPOSURE_END_STAGE_VALUE}
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
            tooltip={EXPOSURE_END_STAGE_UNIT}
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
