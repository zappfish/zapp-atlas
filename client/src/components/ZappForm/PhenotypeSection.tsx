import { Fragment, useState } from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import TextArea from '@/ui/TextArea';
import PhenotypePicker from './PhenotypePicker';
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

import {
  type OBOGraphNode,
} from 'frogpot';

type Props = {
  data: ZappObservation;
  update: (u: (d: ZappObservation) => ZappObservation) => void;
  addPhenotype: () => void;
  removePhenotype: (idx: number) => void;
};

export default function PhenotypeSection({ data, update, addPhenotype, removePhenotype }: Props) {
  const [showNotes, setShowNotes] = useState(false);
  const [modalOpenForIndex, setModalOpenForIndex] = useState<number | null>(null);
  const [selectedZpNode, setSelectedZpNode] = useState<OBOGraphNode | null>(null);

  const openModalFor = (idx: number) => {
    setSelectedZpNode(null);
    setModalOpenForIndex(idx);
  };

  const closeModal = () => {
    setModalOpenForIndex(null);
    setSelectedZpNode(null);
  };

  const confirmSelection = () => {
    if (modalOpenForIndex === null || !selectedZpNode) return;
    const idx = modalOpenForIndex;

    update((d) => ({
      ...d,
      phenotype: {
        ...d.phenotype,
        items: d.phenotype.items.map((it, i) =>
          i === idx ? { ...it, termId: selectedZpNode.uri, termLabel: selectedZpNode.label || undefined } : it
        )
      }
    }));

    closeModal();
  };

  const clearSelectedTerm = (idx: number) => {
    update((d) => ({
      ...d,
      phenotype: {
        ...d.phenotype,
        items: d.phenotype.items.map((it, i) =>
          i === idx ? { ...it, termId: undefined, termLabel: undefined } : it
        )
      }
    }));
  };

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
          <Fragment key={idx}>
            <div className="col-8">
              <Input
                label={`Observed phenotype ${idx + 1} (ontology term)`}
                className="observed-phenotype-input"
                onChange={() => {} }
                onClick={() => openModalFor(idx)}
                placeholder="No phenotype selected"
                tooltip={PHENOTYPE_TERM}
                value={item.termLabel || ''}
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
            <div className="row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <button type="button" onClick={() => openModalFor(idx)}>
                  Select phenotype
                </button>
                <span style={{ marginLeft: 8 }} />
                <button type="button" onClick={() => clearSelectedTerm(idx)}>
                  Clear selected term
                </button>
              </div>
              <div>
                <button type="button" onClick={() => removePhenotype(idx)}>
                  Remove phenotype
                </button>
              </div>
            </div>
          </Fragment>
        ))}
        <div className="row">
          <button type="button" onClick={addPhenotype}>+ Add phenotype</button>
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
              value={data.phenotype.additional_notes || ''}
              onChange={(e) =>
                update((d) => ({
                  ...d,
                  phenotype: { ...d.phenotype, additional_notes: (e.target as HTMLTextAreaElement).value }
                }))
              }
            />
          </div>
        )}
      </FormSection>

      {/* Full-screen-ish modal */}
      {modalOpenForIndex !== null && (
        <div className="phenotype-modal-overlay">
          <div className="phenotype-modal">
            <div className="phenotype-modal-header">Select phenotype</div>
            <div className="phenotype-modal-body">
              <PhenotypePicker
                onSelectNode={node => setSelectedZpNode(node)}
              />
            </div>
            <div className="phenotype-modal-footer">
              <button type="button" onClick={closeModal}>Cancel</button>
              <button type="button" onClick={confirmSelection} disabled={!selectedZpNode}>Select phenotype</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
