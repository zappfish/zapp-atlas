import { useRef, useState } from "react";
import { GraphNode, OBOGraphNode, HierarchyTree, HierarchyTreeHandle, useNodeSearch } from "frogpot"
import { useZPGraph } from "@/hooks";

type PhenotypePickerProps = {
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
  const zfaSearch = useNodeSearch(result.loading ? [] : result.zfaHierarchy.items())
  const zpSearch = useNodeSearch(result.loading ? [] : result.zpHierarchy.items())
  const treeRef = useRef<HierarchyTreeHandle | null>(null)
  const [currentZPPhenotypes, setCurrentZPPhenotypes] = useState<OBOGraphNode[]>([]);
  const [selectedZFANode, setSelectedZFANode] = useState<GraphNode | null>(null);
  const [selectedZpNode, setSelectedZpNode] = useState<OBOGraphNode | null>(null);
  const [searchPhenotypesByZFA, setSearchPhenotypesByZFA] = useState(false);
  const anatomyPhenotypeSearch = useNodeSearch(currentZPPhenotypes)

  if (result.loading) {
    return "Loading zebrafish ontologies...";
  }

  const { zfaHierarchy, zpByZFA } = result

  let phenotypeResults: OBOGraphNode[]

  if (zpSearch.query) {
    if (searchPhenotypesByZFA) {
      phenotypeResults = anatomyPhenotypeSearch.results?.map(n => n.node) || [];
    } else {
      phenotypeResults = zpSearch.results?.map(n => n.node).slice(0, 50) || [];
    }
  } else {
    phenotypeResults = currentZPPhenotypes;
  }

  return (
    <>
      <div className="phenotype-pane">
        <div className="phenotype-pane-header">Zebrafish anatomy</div>
        <div className="phenotype-pane-content">
          <div>
            <input
              style={{
                width: "100%",
              }}
              type="text"
              value={zfaSearch.query}
              placeholder="Search for a Zebrafish anatomical entity to filter phenotypes"
              onChange={e => { zfaSearch.setQuery(e.target.value) }}
            />
          </div>
          <div className="phenotype-pane-content">
            <button
              onClick={() => {
                treeRef.current?.reset();
                setCurrentZPPhenotypes([]);
                setSelectedZFANode(null);
              }}
            >Reset</button>
          </div>
          <div style={{
            position: "relative",
          }}>
            <div style={{
              padding: "0 1rem",
              position: "absolute",
              zIndex: 1,
              background: "white",
              width: '100%',
            }}>
              {zfaSearch.results === null ? null : zfaSearch.results.slice(0, 50).map(result =>
              <div
                key={result.node.uri}
                className="phenotype-item"
                onClick={() => {
                  const nodes = zpByZFA?.get(result.node.uri);

                  treeRef.current?.showNode(result.node.uri);
                  zfaSearch.setQuery("");

                  if (!nodes) {
                    setCurrentZPPhenotypes([]);
                  } else {
                    nodes.sort((nodeA, nodeB) => {
                      return getZfinUsage(nodeB) - getZfinUsage(nodeA);
                    })
                    setCurrentZPPhenotypes(nodes);
                  }
                }}
                style={{
                  cursor: "pointer",
                }}
              >
                <label>{zfaSearch.highlightText(result.node.label || "")}</label>
                {result.node.synonyms.length === 0 ? null : (
                  <div>
                    {result.node.synonyms.map(synonym => (
                      <div>{zfaSearch.highlightText(synonym.value)}</div>
                    ))}
                  </div>
                )}
                {result.node.definitions.length === 0 ? null : (
                  <div>
                    <br />
                    {result.node.definitions.map(synonym => (
                      <div>{zfaSearch.highlightText(synonym.value)}</div>
                    ))}
                  </div>
                )}
              </div>
              )}
            </div>
          </div>
          <HierarchyTree
            key={zfaHierarchy.root.uri}
            ref={treeRef}
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

              // FIXME: Why is this typed as GraphNode and not OBOGraphNode?
              setSelectedZFANode(node);
              setSelectedZpNode(null);
            }}
          />
        </div>
      </div>

      <div className="phenotype-pane">
        <div className="phenotype-pane-header">Phenotypes</div>
        <div className="phenotype-pane-content">
          <div>
            <input
              style={{
                width: "100%",
              }}
              type="text"
              value={zpSearch.query}
              placeholder="Search for Zebrafish phenotypes"
              onChange={e => {
                zpSearch.setQuery(e.target.value);
                anatomyPhenotypeSearch.setQuery(e.target.value);
              }}
            />
          </div>
          <div className="phenotype-pane-content">
            <label>
              <input
                type="checkbox"
                checked={searchPhenotypesByZFA}
                onChange={() => {
                  setSearchPhenotypesByZFA(prev => !prev)
                }}
              >
              </input>
              Limit to selected anatomical entity
            </label>
          </div>
          <ul className="phenotype-list">
            {
              phenotypeResults.map((node) => (
                <li
                  key={node.uri}
                  className={'phenotype-item' + (selectedZpNode?.uri === node.uri ? ' active' : '')}
                  onClick={() => {
                    setSelectedZpNode(node)
                    props.onSelectNode?.(node)
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{node.label}</div>
                  {selectedZpNode?.uri !== node.uri ? null : (
                    <div>
                      {node.synonyms.length === 0 ? null : (
                        <div>
                          <div style={{ fontWeight: 500, margin: ".5rem 0", }}>Synonyms</div>
                          <ul>
                          {node.synonyms.map(synonym => (
                            <li key={synonym.value}>{synonym.value}</li>
                          ))}
                          </ul>
                        </div>
                      )}
                      {node.definitions.length === 0 ? null : (
                        <div>
                          <div style={{ fontWeight: 500, marginTop: ".5rem 0", }}>Definition</div>
                          {node.definitions.map(definition => (
                            <div style={{ paddingLeft: "40px" }} key={definition.value}>{definition.value}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                  <div style={{ fontSize: 12, color: '#555' }}>{node.uri}</div>
                  <div style={{ fontSize: 12, color: '#555' }}>
                    ZFin usages: {getZfinUsage(node)}
                  </div>
                </li>
              ))
            }
          </ul>
        </div>
      </div>
    </>
  )
}
