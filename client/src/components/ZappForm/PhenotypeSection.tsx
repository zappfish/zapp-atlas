import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import TextArea from '@/ui/TextArea';
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
  Hierarchy,
  HierarchyTree ,
  OBOGraphLoader,
  type OBOGraphNode,
} from 'zapp-hierarchy-browser';

type Props = {
  data: ZappObservation;
  update: (u: (d: ZappObservation) => ZappObservation) => void;
  addPhenotype: () => void;
  removePhenotype: (idx: number) => void;
};

function getZfinUsage(node: OBOGraphNode) {
  const bpvs = node.meta?.basicPropertyValues || [];

  const zfinUsageBPV = bpvs.find(bpv =>
    bpv.pred === "http://purl.obolibrary.org/obo/terms_isReferencedBy" &&
    bpv.val === "http://purl.obolibrary.org/obo/infores_zfin"
  );

  if (!zfinUsageBPV) return 0;

  const usageMetaBPV = zfinUsageBPV.meta?.basicPropertyValues || [];

  const zfinUsageNumber = usageMetaBPV.find(
    bpv => bpv.pred == "http://www.geneontology.org/formats/oboInOwl#zapp:hasReferenceCount"
  )

  if (!zfinUsageNumber) return 0;

  return parseInt(zfinUsageNumber.val)

}

export default function PhenotypeSection({ data, update, addPhenotype, removePhenotype }: Props) {
  const [showNotes, setShowNotes] = React.useState(false);

  // Modal + ontology state
  const [modalOpenForIndex, setModalOpenForIndex] = React.useState<number | null>(null);
  const [loadingOntologies, setLoadingOntologies] = React.useState(false);
  const [zfaHierarchy, setZfaHierarchy] = React.useState<Hierarchy<OBOGraphNode> | null>(null);
  const [zpByZFA, setZpByZFA] = React.useState<Map<string, OBOGraphNode[]> | null>(null);
  const [currentZPPhenotypes, setCurrentZPPhenotypes] = React.useState<OBOGraphNode[]>([]);
  const [selectedZpNode, setSelectedZpNode] = React.useState<OBOGraphNode | null>(null);

  // Lazy-load ontologies the first time the modal is opened
  React.useEffect(() => {
    if (modalOpenForIndex !== null && !zfaHierarchy) {
      let cancelled = false;
      (async () => {
        try {
          setLoadingOntologies(true);
          const loader = new OBOGraphLoader();
          const graph = await loader.fromURI('data/zfa.json');
          const zpGraph = await loader.fromURI('data/zp-zapp.json');
          const zpRoot = zpGraph.getItem('http://purl.obolibrary.org/obo/ZP_0000000');
          const zfaPreferredRoot = 'http://purl.obolibrary.org/obo/ZFA_0001439';

          const zpItems = zpGraph.findAllChildren(zpRoot);
          const zfaItemsByZFA = new Map<string, OBOGraphNode[]>();

          zpItems.forEach((node) => {
            (node.edges || [])
              .filter((edge) => edge.pred === 'http://purl.obolibrary.org/obo/UPHENO_0000003')
              .forEach((edge) => {
                if (!zfaItemsByZFA.has(edge.obj)) {
                  zfaItemsByZFA.set(edge.obj, []);
                }
                zfaItemsByZFA.get(edge.obj)!.push(node);
              });
          });

          const hierarchy = graph.getHierarchy(zfaPreferredRoot);

          if (!cancelled) {
            setZfaHierarchy(hierarchy);
            setZpByZFA(zfaItemsByZFA);
          }
        } catch (e) {
          console.error('Failed to load ontologies', e);
        } finally {
          if (!cancelled) setLoadingOntologies(false);
        }
      })();

      return () => {
        cancelled = true;
      };
    }
  }, [modalOpenForIndex, zfaHierarchy]);

  const openModalFor = (idx: number) => {
    setSelectedZpNode(null);
    setCurrentZPPhenotypes([]);
    setModalOpenForIndex(idx);
  };

  const closeModal = () => {
    setModalOpenForIndex(null);
    setSelectedZpNode(null);
    setCurrentZPPhenotypes([]);
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
          <React.Fragment key={idx}>
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
          </React.Fragment>
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
              <div className="phenotype-pane">
                <div className="phenotype-pane-header">ZFA anatomy</div>
                <div className="phenotype-pane-content">
                  {loadingOntologies && !zfaHierarchy ? (
                    <div>Loading ontologies…</div>
                  ) : null}
                  {zfaHierarchy ? (
                    <HierarchyTree
                      key={zfaHierarchy.root.uri}
                      width={600}
                      hierarchy={zfaHierarchy}
                      rootURI={zfaHierarchy.root.uri}
                      itemURI={zfaHierarchy.root.uri}
                      onSelectNode={(node) => {
                        const nodes = zpByZFA?.get(node.uri);
                        if (!nodes) {
                          setCurrentZPPhenotypes([]);
                        } else {
                          nodes.sort((nodeA, nodeB) => {
                            return getZfinUsage(nodeB) - getZfinUsage(nodeA);
                          })
                          setCurrentZPPhenotypes(nodes);
                        }
                        setSelectedZpNode(null);
                      }}
                    />
                  ) : null}
                </div>
              </div>

              <div className="phenotype-pane">
                <div className="phenotype-pane-header">Phenotypes</div>
                <div className="phenotype-pane-content">
                  <ul className="phenotype-list">
                    {currentZPPhenotypes.length === 0 ? (
                      <li className="phenotype-item" style={{ cursor: 'default' }}>
                        Select an anatomy term to view phenotypes
                      </li>
                    ) : (
                      currentZPPhenotypes.map((node) => (
                        <li
                          key={node.uri}
                          className={'phenotype-item' + (selectedZpNode?.uri === node.uri ? ' active' : '')}
                          onClick={() => setSelectedZpNode(node)}
                        >
                          <div style={{ fontWeight: 600 }}>{node.label}</div>
                          <div style={{ fontSize: 12, color: '#555' }}>{node.uri}</div>
                          <div style={{ fontSize: 12, color: '#555' }}>
                            ZFin usages: {getZfinUsage(node)}
                          </div>
                        </li>
                      ))
                    )}
                  </ul>
                </div>
              </div>
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
