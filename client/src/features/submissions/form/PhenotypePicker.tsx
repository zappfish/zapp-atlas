import { useMemo, useRef, useState } from "react";
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
  PickerCount,
  PickerFilter,
  PickerFilterClear,
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

/** Rendering thousands of rows is slow and nobody scrolls that far. */
const MAX_SHOWN = 200;

/** http://purl.obolibrary.org/obo/ZP_0000055 -> ZP:0000055 */
const curieOf = (uri: string) => uri.replace(OBO, "").replace("_", ":");

type Anatomy = { uri: string; label: string };

/**
 * Choose a ZP phenotype, by searching for it or by way of the anatomy it
 * affects. Choosing a ZFA term narrows the phenotype list to that term and,
 * unless "only this term" is checked, its parts and subtypes. The phenotype
 * search then searches within that list; clearing the anatomy searches every
 * phenotype again.
 *
 * Without a search, phenotypes are listed most curated by ZFIN first.
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
  const treeRef = useRef<HierarchyTreeHandle | null>(null);
  const [anatomy, setAnatomy] = useState<Anatomy | null>(null);
  const [isExactOnly, setIsExactOnly] = useState(false);
  const [selectedZpNode, setSelectedZpNode] = useState<OBOGraphNode | null>(null);

  // The query's data, not `result`: that is a new object every render, and
  // a new list every render would rebuild the search index below each time.
  const zfaGraph = result.loading ? null : result.zfaGraph;
  const zpByZFA = result.loading ? null : result.zpByZFA;

  // The phenotypes of the chosen anatomy: those associated with the term
  // itself, and unless isExactOnly, those of everything below it in the
  // tree (is_a and part_of, the relations the tree is drawn from).
  const anatomyPhenotypes = useMemo(() => {
    if (!zfaGraph || !zpByZFA || !anatomy) return [];
    const terms = [anatomy.uri];
    if (!isExactOnly) {
      terms.push(...zfaGraph.findAllChildren(zfaGraph.getItem(anatomy.uri)).map((n) => n.uri));
    }
    const found = new Map<string, OBOGraphNode>();
    for (const term of terms) {
      for (const node of zpByZFA.get(term) ?? []) found.set(node.uri, node);
    }
    return [...found.values()];
  }, [zfaGraph, zpByZFA, anatomy, isExactOnly]);

  const zfaSearch = useNodeSearch(result.loading ? [] : result.zfaHierarchy.items());
  const zpSearch = useNodeSearch(result.loading ? [] : result.zpHierarchy.items());
  const anatomyPhenotypeSearch = useNodeSearch(anatomyPhenotypes);

  if (result.loading) {
    return <SearchHint role="status">Loading zebrafish ontologies…</SearchHint>;
  }

  const { zfaHierarchy, zfinCounts } = result;
  const usage = (node: OBOGraphNode) => zfinCounts.get(node.uri) ?? 0;
  const byUsage = (a: OBOGraphNode, b: OBOGraphNode) => usage(b) - usage(a);

  const query = zpSearch.query.trim();
  const search = anatomy ? anatomyPhenotypeSearch : zpSearch;

  // A search lists best matches first, and among equal matches the more
  // curated; no search lists the chosen anatomy's phenotypes by usage.
  // frogpot puts an exact label match first, so it stays there.
  let phenotypes: OBOGraphNode[];
  if (query) {
    const results = search.results ?? [];
    const exact = results[0]?.node.label === search.query ? results.slice(0, 1) : [];
    const rest = results
      .slice(exact.length)
      .sort((a, b) => b.score - a.score || byUsage(a.node, b.node));
    phenotypes = [...exact, ...rest].map((r) => r.node);
  } else {
    phenotypes = [...anatomyPhenotypes].sort(byUsage);
  }
  const shown = phenotypes.slice(0, MAX_SHOWN);

  const chooseAnatomy = (node: { uri: string; label: string | null }) => {
    setAnatomy({ uri: node.uri, label: node.label ?? curieOf(node.uri) });
  };

  const emptyMessage = query
    ? `No phenotypes match “${query}”${anatomy ? ` in “${anatomy.label}”` : ""}.`
    : anatomy
      ? `No phenotypes are associated with “${anatomy.label}”${isExactOnly ? " itself" : " or its parts and subtypes"}.`
      : "Search for a phenotype, or choose an anatomical entity to list its phenotypes.";

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
                        chooseAnatomy(node);
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
        </PickerTools>
        <PickerPaneBody>
          <HierarchyTree
            key={zfaHierarchy.root.uri}
            ref={treeRef}
            hierarchy={zfaHierarchy}
            rootURI={zfaHierarchy.root.uri}
            onSelectNode={chooseAnatomy}
          />
        </PickerPaneBody>
      </PickerPane>

      <PickerPane>
        <PickerPaneHead>Phenotypes</PickerPaneHead>
        <PickerTools>
          {anatomy && (
            <>
              <PickerFilter>
                <span>
                  Phenotypes of <strong>{anatomy.label}</strong>
                </span>
                <PickerFilterClear
                  type="button"
                  onClick={() => setAnatomy(null)}
                  aria-label={`Show phenotypes of all anatomy, not just ${anatomy.label}`}
                  title="Clear"
                >
                  ✕
                </PickerFilterClear>
              </PickerFilter>
              <PickerCheck>
                <input
                  type="checkbox"
                  checked={isExactOnly}
                  onChange={() => setIsExactOnly((was) => !was)}
                />{" "}
                Only “{anatomy.label}” itself, not its parts and subtypes
              </PickerCheck>
            </>
          )}
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
              placeholder={
                anatomy
                  ? `Search phenotypes of ${anatomy.label}`
                  : "Search all zebrafish phenotypes"
              }
            />
            {zpSearch.query && (
              <SearchClear
                type="button"
                onClick={() => {
                  zpSearch.setQuery("");
                  anatomyPhenotypeSearch.setQuery("");
                }}
                aria-label="Clear the search"
              >
                ✕
              </SearchClear>
            )}
          </SearchBox>
          {phenotypes.length > 0 && (
            <PickerCount role="status">
              {phenotypes.length > MAX_SHOWN
                ? `Showing ${MAX_SHOWN} of ${phenotypes.length} phenotypes${query ? "" : ", most used first"}. Search to narrow.`
                : `${phenotypes.length} phenotype${phenotypes.length === 1 ? "" : "s"}`}
            </PickerCount>
          )}
        </PickerTools>
        <PickerPaneBody>
          {shown.length === 0 ? (
            <SearchHint>{emptyMessage}</SearchHint>
          ) : (
            <PhenotypeList>
              {shown.map((node) => {
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
