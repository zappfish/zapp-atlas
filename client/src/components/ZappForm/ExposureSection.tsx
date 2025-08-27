import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import type { ZappObservation } from '@/schema';
import {
  SUBSTANCE_IDTYPE_OPTIONS,
  CONC_UNIT_OPTIONS,
  EXPOSURE_ROUTE_OPTIONS,
  EXPOSURE_TYPE_OPTIONS,
  PATTERN_OPTIONS,
  STAGE_UNIT_OPTIONS
} from './constants';

export default function ExposureSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  const route = data.exposure.route;
  const type = data.exposure.type;

  return (
    <div className="row">
      <FormSection title="Exposure Event">
        <div className="col-5">
          <Input
            label="Substance name"
            placeholder="Chemical name"
            value={data.exposure.substance.name || ''}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  substance: { ...d.exposure.substance, name: e.target.value }
                }
              }))
            }
          />
        </div>
        <div className="col-3">
          <Select
            label="Identifier type"
            value={data.exposure.substance.idType}
            options={SUBSTANCE_IDTYPE_OPTIONS}
            onChange={(e) => {
              const idType = (e.target as HTMLSelectElement).value as any;
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  substance: {
                    ...d.exposure.substance,
                    idType,
                    id: idType === 'None' ? '' : d.exposure.substance.id
                  }
                }
              }));
            }}
          />
        </div>
        <div className="col-4">
          <Input
            label="Identifier value"
            placeholder="e.g., 2244 (PubChem), 50-00-0 (CAS), CHEBI:15377"
            value={data.exposure.substance.id || ''}
            onChange={(e) =>
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  substance: { ...d.exposure.substance, id: e.target.value }
                }
              }))
            }
            disabled={data.exposure.substance.idType === 'None'}
          />
        </div>

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
                    unit: (e.target as HTMLSelectElement).value as any
                  }
                }
              }))
            }
          />
        </div>

        <div className="col-6">
          <Select
            label="Exposure route"
            value={data.exposure.route || ''}
            options={EXPOSURE_ROUTE_OPTIONS}
            onChange={(e) => {
              const routeVal = (e.target as HTMLSelectElement).value as any;
              update((d) => ({
                ...d,
                exposure: {
                  ...d.exposure,
                  route: routeVal || null,
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
        </div>

        {route === 'water' && (
          <>
            <div className="col-4">
              <Select
                label="Exposure type"
                value={data.exposure.type || ''}
                options={[{ value: '', label: 'Select type' }, ...EXPOSURE_TYPE_OPTIONS]}
                onChange={(e) =>
                  update((d) => ({
                    ...d,
                    exposure: {
                      ...d.exposure,
                      type: (e.target as HTMLSelectElement).value as any,
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
            </div>
            {type === 'continuous' && (
              <div className="col-4">
                <Select
                  label="Exposure pattern"
                  value={data.exposure.pattern || ''}
                  options={[{ value: '', label: 'Select pattern' }, ...PATTERN_OPTIONS]}
                  onChange={(e) =>
                    update((d) => ({
                      ...d,
                      exposure: {
                        ...d.exposure,
                        pattern: (e.target as HTMLSelectElement).value as any
                      }
                    }))
                  }
                />
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
            <div className="col-4">
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
            <div className="col-4">
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
                    unit: (e.target as HTMLSelectElement).value as any
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
                    unit: (e.target as HTMLSelectElement).value as any
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
