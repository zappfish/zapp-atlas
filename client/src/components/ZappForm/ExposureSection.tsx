import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import TextArea from '@/ui/TextArea';
import Tooltip from '@/ui/Tooltip';
import type { ZappObservation } from '@/schema';
import { PATTERN_OPTIONS, STAGE_UNIT_OPTIONS, DURATION_UNIT_OPTIONS } from './constants';
import SubstanceFields from './SubstanceFields';
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
  EXPOSURE_REP_TOTAL_LENGTH,
  EXPOSURE_START_STAGE_VALUE,
  EXPOSURE_START_STAGE_UNIT,
  EXPOSURE_END_STAGE_VALUE,
  EXPOSURE_END_STAGE_UNIT
} from './explanations';

type ExposureEvent = ZappObservation['exposures'][number];
type ExposureRoute = 'water' | 'injected' | 'ingested' | 'gavage';
type ExposurePattern = 'static' | 'static_renewal' | 'flow_through';
type StageUnit = 'hpf' | 'dpf' | 'month';
type DurationUnit = 'minute' | 'hour' | 'day';

function RepeatedExposureFields({
  route,
  repeated,
  onChange
}: {
  route: ExposureRoute;
  repeated: ExposureEvent['repeated'];
  onChange: (rep: ExposureEvent['repeated']) => void;
}) {
  const disableDuration = route !== 'water';



  const updateRepeated = (patch: Partial<ExposureEvent['repeated']>) => {
    onChange({ ...repeated, ...patch });
  };

  return (
    <>
      <div className="col-4">
        <Input
          label="Duration per exposure"
          type="number"
          tooltip={EXPOSURE_REP_DURATION_PER}
          disabled={disableDuration}
          value={repeated.duration_per.value ?? ''}
          onChange={(e) => {
            if (disableDuration) return;
            updateRepeated({
              duration_per: {
                ...repeated.duration_per,
                value: e.currentTarget.value === '' ? null : Number(e.currentTarget.value)
              }
            });
          }}
        />
      </div>
      <div className="col-2">
        <Select
          label="Unit"
          disabled={disableDuration}
          value={repeated.duration_per.unit || ''}
          options={DURATION_UNIT_OPTIONS}
          onChange={(e) =>
            updateRepeated({
              duration_per: {
                ...repeated.duration_per,
                unit: (e.target as HTMLSelectElement).value as DurationUnit
              }
            })
          }
        />
      </div>

      <div className="col-6">
        <Input
          label="Number of exposures"
          type="number"
          tooltip={EXPOSURE_REP_FREQUENCY}
          value={repeated.count ?? ''}
          onChange={(e) =>
            updateRepeated({
              count: e.currentTarget.value === '' ? null : Number(e.currentTarget.value)
            })
          }
        />
      </div>

      <div className="col-4">
        <Input
          label="Interval between exposures"
          type="number"
          tooltip={EXPOSURE_REP_INTERVAL}
          value={repeated.interval_between.value ?? ''}
          onChange={(e) =>
            updateRepeated({
              interval_between: {
                ...repeated.interval_between,
                value: e.currentTarget.value === '' ? null : Number(e.currentTarget.value)
              }
            })
          }
        />
      </div>
      <div className="col-2">
        <Select
          label="Unit"
          value={repeated.interval_between.unit || ''}
          options={DURATION_UNIT_OPTIONS}
          onChange={(e) =>
            updateRepeated({
              interval_between: {
                ...repeated.interval_between,
                unit: (e.target as HTMLSelectElement).value as DurationUnit
              }
            })
          }
        />
      </div>

      <div className="col-4">
        <Input
          label="Total length of exposure"
          type="number"
          tooltip={EXPOSURE_REP_TOTAL_LENGTH}
          value={repeated.total_length.value ?? ''}
          onChange={(e) =>
            updateRepeated({
              total_length: {
                ...repeated.total_length,
                value: e.currentTarget.value === '' ? null : Number(e.currentTarget.value)
              }
            })
          }
        />
      </div>
      <div className="col-2">
        <Select
          label="Unit"
          value={repeated.total_length.unit || ''}
          options={DURATION_UNIT_OPTIONS}
          onChange={(e) =>
            updateRepeated({
              total_length: {
                ...repeated.total_length,
                unit: (e.target as HTMLSelectElement).value as DurationUnit
              }
            })
          }
        />
      </div>

    </>
  );
}

export default function ExposureSection({
  exposure,
  update
}: {
  exposure: ExposureEvent;
  update: (u: (e: ExposureEvent) => ExposureEvent) => void;
}) {
  const route = exposure.route;
  const type = exposure.type;
  const [showNotes, setShowNotes] = React.useState(false);

  const u = exposure.concentration.unit;
  const isCustomUnit = u === '' || (u != null && u !== 'uM' && u !== 'mg/L');

  return (
    <div className="row">
      <FormSection title="Exposure Event">
        <SubstanceFields
          value={exposure.substance}
          onChange={(substance) =>
            update((e) => ({
              ...e,
              substance
            }))
          }
        />

        <div className="col-3">
          <Input
            label="Substance concentration"
            tooltip={EXPOSURE_CONCENTRATION_VALUE}
            type="number"
            placeholder="e.g., 10"
            value={exposure.concentration.value ?? ''}
            onChange={(evt) =>
              update((e) => ({
                ...e,
                concentration: {
                  ...e.concentration,
                  value: evt.currentTarget.value === '' ? null : Number(evt.currentTarget.value)
                }
              }))
            }
          />
        </div>

        <div className="col-3">
          <div className="field">
            <div className="inline">
              <label>Unit</label>
              <Tooltip text={EXPOSURE_CONCENTRATION_UNIT} />
            </div>
            <div className="inline" role="radiogroup" aria-label="Concentration unit">
              {[
                { v: 'uM', label: 'μM' },
                { v: 'mg/L', label: 'mg/L' },
                { v: '__other__', label: 'Other' }
              ].map((opt) => (
                <label key={opt.v} className="inline" style={{ gap: 4 }}>
                  <input
                    type="radio"
                    name="conc-unit"
                    value={opt.v}
                    checked={opt.v === '__other__' ? isCustomUnit : exposure.concentration.unit === opt.v}
                    onChange={(e) => {
                      const val = e.currentTarget.value;
                      update((ex) => {
                        const KNOWN = ['uM', 'mg/L'];
                        return {
                          ...ex,
                          concentration: {
                            ...ex.concentration,
                            unit:
                              val === '__other__'
                                ? (ex.concentration.unit && !KNOWN.includes(ex.concentration.unit) ? ex.concentration.unit : '')
                                : val
                          }
                        };
                      });
                    }}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="col-4">
          {isCustomUnit ? (
            <Input
              label="Custom unit"
              placeholder="Enter unit"
              value={exposure.concentration.unit || ''}
              onChange={(e) =>
                update((ex) => ({
                  ...ex,
                  concentration: {
                    ...ex.concentration,
                    unit: e.currentTarget.value
                  }
                }))
              }
            />
          ) : null}
        </div>

        <div className="col-12">
          <hr />
        </div>

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
                    checked={exposure.route === (opt.value as ExposureRoute)}
                    onChange={(e) => {
                      const routeVal = e.currentTarget.value as ExposureRoute;
                      update((ex) => ({
                        ...ex,
                        route: routeVal,
                        type: null,
                        pattern: null,
                        duration: { value: null, unit: null },
                        repeated: {
                          count: null,
                          duration_per: { value: null, unit: null },
                          interval_between: { value: null, unit: null },
                          total_length: { value: null, unit: null },
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
                        checked={exposure.type === opt.value}
                        onChange={(e) =>
                          update((ex) => {
                            const nextType = e.currentTarget.value as 'continuous' | 'repeated';
                            return {
                              ...ex,
                              type: nextType,
                              pattern: null,
                              duration: nextType === 'continuous' ? ex.duration : { value: null, unit: null },
                              repeated: {
                                count: null,
                                duration_per: { value: null, unit: null },
                                interval_between: { value: null, unit: null },
                                total_length: { value: null, unit: null },
                              }
                            };
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
                    value={exposure.duration.value ?? ''}
                    onChange={(e) =>
                      update((ex) => ({
                        ...ex,
                        duration: {
                          ...ex.duration,
                          value: e.currentTarget.value === '' ? null : Number(e.currentTarget.value)
                        }
                      }))
                    }
                  />
                </div>
                <div className="col-2">
                  <Select
                    label="Unit"
                    tooltip={EXPOSURE_DURATION_UNIT}
                    value={exposure.duration.unit || ''}
                    options={DURATION_UNIT_OPTIONS}
                    onChange={(e) =>
                      update((ex) => ({
                        ...ex,
                        duration: {
                          ...ex.duration,
                          unit: (e.target as HTMLSelectElement).value as DurationUnit
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
                    <div className="inline" role="group" aria-label="Exposure pattern">
                      {PATTERN_OPTIONS.map((opt) => (
                        <label key={opt.value} className="inline" style={{ gap: 4 }}>
                          <input
                            type="checkbox"
                            name={`exposure-pattern-${opt.value}`}
                            value={opt.value}
                            checked={exposure.pattern === opt.value}
                            onChange={() =>
                              update((ex) => ({
                                ...ex,
                                pattern: ex.pattern === opt.value ? null : (opt.value as ExposurePattern)
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
              <RepeatedExposureFields
                route={route}
                repeated={exposure.repeated}
                onChange={(rep) =>
                  update((ex) => ({
                    ...ex,
                    repeated: rep
                  }))
                }
              />
            )}
          </>
        )}

        {route && route !== 'water' && (
          <>
            <div className="col-12">
              <div className="field">
                <div className="inline">
                  <label>Exposure regimen</label>
                  <Tooltip text={EXPOSURE_REGIMEN} />
                </div>
                <div className="inline" role="radiogroup" aria-label="Exposure regimen">
                  {[
                    { value: 'single', label: 'Single exposure' },
                    { value: 'repeated', label: 'Repeated exposures' }
                  ].map((opt) => (
                    <label key={opt.value} className="inline" style={{ gap: 4 }}>
                      <input
                        type="radio"
                        name="exposure-type-nonwater"
                        value={opt.value}
                        checked={opt.value === 'single' ? exposure.type === null : exposure.type === 'repeated'}
                        onChange={(e) =>
                          update((ex) => {
                            const isRepeated = e.currentTarget.value === 'repeated';
                            return {
                              ...ex,
                              type: isRepeated ? 'repeated' : null,
                              repeated: {
                                count: null,
                                duration_per: { value: null, unit: null },
                                interval_between: { value: null, unit: null },
                                total_length: { value: null, unit: null },
                              }
                            };
                          })
                        }
                      />
                      {opt.label}
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {exposure.type === 'repeated' && (
              <RepeatedExposureFields
                route={route}
                repeated={exposure.repeated}
                onChange={(rep) =>
                  update((ex) => ({
                    ...ex,
                    repeated: rep
                  }))
                }
              />
            )}
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
            value={exposure.start_stage.value ?? ''}
            onChange={(e) =>
              update((ex) => ({
                ...ex,
                start_stage: {
                  ...ex.start_stage,
                  value: e.currentTarget.value === '' ? null : Number(e.currentTarget.value)
                }
              }))
            }
          />
        </div>
        <div className="col-3">
          <Select
            label="Start stage unit"
            value={exposure.start_stage.unit || ''}
            options={STAGE_UNIT_OPTIONS}
            tooltip={EXPOSURE_START_STAGE_UNIT}
            onChange={(e) =>
              update((ex) => ({
                ...ex,
                start_stage: {
                  ...ex.start_stage,
                  unit: (e.target as HTMLSelectElement).value as StageUnit
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
            value={exposure.end_stage.value ?? ''}
            onChange={(e) =>
              update((ex) => ({
                ...ex,
                end_stage: {
                  ...ex.end_stage,
                  value: e.currentTarget.value === '' ? null : Number(e.currentTarget.value)
                }
              }))
            }
          />
        </div>
        <div className="col-3">
          <Select
            label="End stage unit"
            value={exposure.end_stage.unit || ''}
            options={STAGE_UNIT_OPTIONS}
            tooltip={EXPOSURE_END_STAGE_UNIT}
            onChange={(e) =>
              update((ex) => ({
                ...ex,
                end_stage: {
                  ...ex.end_stage,
                  unit: (e.target as HTMLSelectElement).value as StageUnit
                }
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
              value={exposure.additional_notes || ''}
              onChange={(e) =>
                update((ex) => ({
                  ...ex,
                  additional_notes: (e.target as HTMLTextAreaElement).value
                }))
              }
            />
          </div>
        )}
      </FormSection>
    </div>
  );
}
