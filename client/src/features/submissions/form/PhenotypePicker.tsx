import { useRef, useState } from "react";
import {
  HierarchyTree,
  useNodeSearch,
  type HierarchyTreeHandle,
  type OBOGraphNode,
} from "frogpot";
import { SearchIcon } from "@/components/icons";
import { useZPGraph } from "@/useZPGraph";
import {
  OptionId,
  OptionName,
  OptionText,
  PhenotypeDetail,
  PhenotypeDetailHeading,
  PhenotypeList,
  PhenotypeOption,
  PickerCheck,
  PickerPane,
  PickerPaneBody,
  PickerPaneHead,
  PickerPanes,
  PickerTools,
  SearchBox,
  SearchClear,
  SearchHint,
  SearchIconSlot,
  SearchInput,
  SearchList,
  SearchOption,
} from "@/styles/elements";

const OBO = "http://purl.obolibrary.org/obo/";

/** http://purl.obolibrary.org/obo/ZP_0000055 -> ZP:0000055 */
const curieOf = (uri: string) => uri.replace(OBO, "").replace("_", ":");

/**
 * Choose a ZP phenotype, by searching for it or by way of the anatomy it
 * affects: choosing a ZFA term lists the phenotypes associated with it, most
 * often curated by ZFIN first.
 *
 * The ontologies load the first time this renders and stay loaded for the
 * rest of the visit (see useZPGraph).
 */
const PhenotypePicker = ({
  onSelectNode,
}: {
  onSelectNode?: (node: OBOGraphNode) => void;
}) => {
  const result = useZPGraph();
  const zfaSearch = useNodeSearch(result.loading ? [] : result.zfaHierarchy.items());
  const zpSearch = useNodeSearch(result.loading ? [] : result.zpHierarchy.items());
  const treeRef = useRef<HierarchyTreeHandle | null>(null);
  const [currentZPPhenotypes, setCurrentZPPhenotypes] = useState<OBOGraphNode[]>([]);
  const [selectedZpNode, setSelectedZpNode] = useState<OBOGraphNode | null>(null);
  const [searchPhenotypesByZFA, setSearchPhenotypesByZFA] = useState(false);
  const anatomyPhenotypeSearch = useNodeSearch(currentZPPhenotypes);

  if (result.loading) {
    return <SearchHint role="status">Loading zebrafish ontologies…</SearchHint>;
  }

  const { zfaHierarchy, zpByZFA, zfinCounts } = result;
  const usage = (node: OBOGraphNode) => zfinCounts.get(node.uri) ?? 0;

  /** List the phenotypes of one anatomical entity, most curated first. */
  const showPhenotypesOf = (zfaURI: string) => {
    const nodes = zpByZFA.get(zfaURI) ?? [];
    setCurrentZPPhenotypes([...nodes].sort((a, b) => usage(b) - usage(a)));
    setSelectedZpNode(null);
  };

  const reset = () => {
    treeRef.current?.reset();
    setCurrentZPPhenotypes([]);
  };

  let phenotypeResults: OBOGraphNode[];
  if (zpSearch.query) {
    phenotypeResults = searchPhenotypesByZFA
      ? anatomyPhenotypeSearch.results?.map((r) => r.node) ?? []
      : zpSearch.results?.map((r) => r.node).slice(0, 50) ?? [];
  } else {
    phenotypeResults = currentZPPhenotypes;
  }

  const zfaResults = zfaSearch.results?.slice(0, 50) ?? [];

  return (
    <PickerPanes>
      <PickerPane>
        <PickerPaneHead>Zebrafish anatomy</PickerPaneHead>
        <PickerTools>
          <SearchBox>
            <SearchIconSlot aria-hidden="true">
              <SearchIcon />
            </SearchIconSlot>
            <SearchInput
              value={zfaSearch.query}
              onChange={(e) => zfaSearch.setQuery(e.target.value)}
              aria-label="Search for an anatomical entity"
              placeholder="Search for an anatomical entity to filter phenotypes"
            />
            {zfaSearch.query && (
              <SearchClear
                type="button"
                onClick={() => zfaSearch.setQuery("")}
                aria-label="Clear the search"
              >
                ✕
              </SearchClear>
            )}
            {zfaResults.length > 0 && (
              <SearchList role="listbox">
                {zfaResults.map(({ node }) => (
                  <li key={node.uri}>
                    <SearchOption
                      type="button"
                      onClick={() => {
                        treeRef.current?.showNode(node.uri);
                        zfaSearch.setQuery("");
                        showPhenotypesOf(node.uri);
                      }}
                    >
                      <OptionText>
                        <OptionName>{zfaSearch.highlightText(node.label || "")}</OptionName>
                        {node.synonyms.length > 0 && (
                          <OptionId>
                            {node.synonyms.map((synonym) => synonym.value).join(", ")}
                          </OptionId>
                        )}
                      </OptionText>
                    </SearchOption>
                  </li>
                ))}
              </SearchList>
            )}
          </SearchBox>
          <div>
            <button className="btn btn--neutral" type="button" onClick={reset}>
              Reset
            </button>
          </div>
        </PickerTools>
        <PickerPaneBody>
          <HierarchyTree
            key={zfaHierarchy.root.uri}
            ref={treeRef}
            hierarchy={zfaHierarchy}
            rootURI={zfaHierarchy.root.uri}
            onSelectNode={(node) => showPhenotypesOf(node.uri)}
          />
        </PickerPaneBody>
      </PickerPane>

      <PickerPane>
        <PickerPaneHead>Phenotypes</PickerPaneHead>
        <PickerTools>
          <SearchBox>
            <SearchIconSlot aria-hidden="true">
              <SearchIcon />
            </SearchIconSlot>
            <SearchInput
              value={zpSearch.query}
              onChange={(e) => {
                zpSearch.setQuery(e.target.value);
                anatomyPhenotypeSearch.setQuery(e.target.value);
              }}
              aria-label="Search for a phenotype"
              placeholder="Search for zebrafish phenotypes"
            />
          </SearchBox>
          <PickerCheck>
            <input
              type="checkbox"
              checked={searchPhenotypesByZFA}
              onChange={() => setSearchPhenotypesByZFA((was) => !was)}
            />{" "}
            Limit to the selected anatomical entity
          </PickerCheck>
        </PickerTools>
        <PickerPaneBody>
          {phenotypeResults.length === 0 ? (
            <SearchHint>
              {zpSearch.query
                ? "No phenotypes match that search."
                : "Choose an anatomical entity, or search, to list phenotypes."}
            </SearchHint>
          ) : (
            <PhenotypeList>
              {phenotypeResults.map((node) => {
                const isActive = selectedZpNode?.uri === node.uri;
                return (
                  <li key={node.uri}>
                    <PhenotypeOption
                      type="button"
                      isActive={isActive}
                      aria-pressed={isActive}
                      onClick={() => {
                        setSelectedZpNode(node);
                        onSelectNode?.(node);
                      }}
                    >
                      <OptionName>{node.label}</OptionName>
                      <OptionId>
                        {curieOf(node.uri)} · ZFIN usages: {usage(node)}
                      </OptionId>
                    </PhenotypeOption>
                    {isActive && (
                      <PhenotypeDetail>
                        {node.synonyms.length > 0 && (
                          <>
                            <PhenotypeDetailHeading>Synonyms</PhenotypeDetailHeading>
                            <ul>
                              {node.synonyms.map((synonym) => (
                                <li key={synonym.value}>{synonym.value}</li>
                              ))}
                            </ul>
                          </>
                        )}
                        {node.definitions.length > 0 && (
                          <>
                            <PhenotypeDetailHeading>Definition</PhenotypeDetailHeading>
                            {node.definitions.map((definition) => (
                              <p key={definition.value}>{definition.value}</p>
                            ))}
                          </>
                        )}
                      </PhenotypeDetail>
                    )}
                  </li>
                );
              })}
            </PhenotypeList>
          )}
        </PickerPaneBody>
      </PickerPane>
    </PickerPanes>
  );
};

export default PhenotypePicker;
