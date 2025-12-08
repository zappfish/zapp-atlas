import { useState } from "react";
import { Graph, OBOGraphNode, HierarchyTree } from "frogpot"
import { useZPGraph } from "@/hooks";

type PhenotypePickerProps = {
  zpGraph: Graph<OBOGraphNode>;
  onSelectNode?: (node: OBOGraphNode) => void;
}

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

export default function PhenotypePicker(props: PhenotypePickerProps) {
  const result = useZPGraph();
  const [currentZPPhenotypes, setCurrentZPPhenotypes] = useState<OBOGraphNode[]>([]);
  const [selectedZpNode, setSelectedZpNode] = useState<OBOGraphNode | null>(null);

  if (result.loading) {
    return "Loading zebrafish ontologies...";
  }


  const { zpHierarchy, zfaHierarchy, zpByZFA } = result

  return (
    <>
      <div className="phenotype-pane">
        <div className="phenotype-pane-header">ZFA anatomy</div>
        <div className="phenotype-pane-content">
          <HierarchyTree
            key={zfaHierarchy.root.uri}
            width={600}
            hierarchy={zfaHierarchy}
            rootURI={zfaHierarchy.root.uri}
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
                  onClick={() => {
                    setSelectedZpNode(node)
                    props.onSelectNode?.(node)
                  }}
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
    </>
  )
}
