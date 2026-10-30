import { useMemo, useRef, useState, type ReactNode } from "react";
import {
  HierarchyTree,
  useNodeSearch,
  type HierarchyTreeHandle,
  type OBOGraphNode,
} from "frogpot";
import { SearchIcon } from "@/components/icons";
import { useZPGraph } from "@/useZPGraph";
import { curieOf } from "./curie";
import {
  Empty,
  EmptyText,
  EmptyTitle,
  OptionId,
  OptionName,
  OptionText,
  PhenotypeDetail,
  PhenotypeDetailHeading,
  PhenotypeList,
  PhenotypeOption,
  PickerCheck,
  PickerLead,
  PickerCount,
  PickerFilter,
  PickerPane,
  PickerPaneBody,
  PickerPaneHead,
  PickerPanes,
  PickerTools,
  PickerView,
  PickerViewHint,
  PickerViews,
  SearchBox,
  SearchClear,
  SearchHint,
  SearchIconSlot,
  SearchInput,
  SearchList,
  SearchOption,
} from "@/styles/elements";

/** Rendering thousands of rows is slow and nobody scrolls that far. */
const MAX_SHOWN = 200;

type Anatomy = { uri: string; label: string };

/** A search box; `children` is whatever hangs off it, such as a results list. */
const PickerSearch = ({
  value,
  onChange,
  label,
  placeholder,
  children,
}: {
  value: string;
  onChange: (value: string) => void;
  label: string;
  placeholder: string;
  children?: ReactNode;
}) => (
  <SearchBox>
    <SearchIconSlot aria-hidden="true">
      <SearchIcon />
    </SearchIconSlot>
    <SearchInput
      value={value}
      onChange={(e) => onChange(e.target.value)}
      aria-label={label}
      placeholder={placeholder}
    />
    {value && (
      <SearchClear
        type="button"
        onClick={() => onChange("")}
        aria-label="Clear the search"
      >
        ✕
      </SearchClear>
    )}
    {children}
  </SearchBox>
);

/**
 * Choose a ZP phenotype, by way of the anatomy it affects or by searching for
 * it directly. Choosing a ZFA term narrows the phenotype list to that term and,
 * unless "only this term" is checked, its parts and subtypes; the search box
 * then searches within that list. The direct view searches every phenotype.
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
  const [isBrowsing, setIsBrowsing] = useState(true);
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

  const search = isBrowsing ? anatomyPhenotypeSearch : zpSearch;
  const query = search.query.trim();

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
    phenotypes = isBrowsing ? [...anatomyPhenotypes].sort(byUsage) : [];
  }
  const shown = phenotypes.slice(0, MAX_SHOWN);

  const chooseAnatomy = (node: { uri: string; label: string | null }) => {
    setAnatomy({ uri: node.uri, label: node.label ?? curieOf(node.uri) });
  };

  const emptyMessage = query
    ? `No phenotypes match “${query}”${isBrowsing && anatomy ? ` in “${anatomy.label}”` : ""}.`
    : !isBrowsing
      ? "Results appear here as you type."
      : anatomy
        ? `No phenotypes are associated with “${anatomy.label}”${isExactOnly ? " itself" : " or its parts and subtypes"}.`
        : "Choose an anatomical entity to list its phenotypes.";

  const zfaResults = zfaSearch.results?.slice(0, 50) ?? [];

  return (
    <>
      <PickerViews role="group" aria-label="How to find a phenotype">
        <PickerView
          type="button"
          aria-pressed={isBrowsing}
          onClick={() => setIsBrowsing(true)}
        >
          Browse by anatomy
          <PickerViewHint>Explore the anatomy tree</PickerViewHint>
        </PickerView>
        <PickerView
          type="button"
          aria-pressed={!isBrowsing}
          onClick={() => setIsBrowsing(false)}
        >
          Search phenotypes directly
          <PickerViewHint>Search by name or synonym</PickerViewHint>
        </PickerView>
      </PickerViews>
      <PickerPanes className={isBrowsing ? undefined : "is-searching"}>
        <PickerPane hidden={!isBrowsing}>
          <PickerPaneHead>Choose an anatomy term</PickerPaneHead>
          <PickerLead>Search the tree or expand a branch below</PickerLead>
          <PickerTools>
            <PickerSearch
              value={zfaSearch.query}
              onChange={zfaSearch.setQuery}
              label="Search for an anatomical entity"
              placeholder="Search for an anatomical entity to filter phenotypes"
            >
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
            </PickerSearch>
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
          <PickerLead>
            {isBrowsing
              ? "Choose an anatomical entity to list its phenotypes"
              : "Search every zebrafish phenotype"}
          </PickerLead>
          <PickerTools>
            {isBrowsing && anatomy && (
              <>
                <PickerFilter>
                  <span>
                    Phenotypes of <strong>{anatomy.label}</strong>
                  </span>
                  <SearchClear
                    type="button"
                    onClick={() => setAnatomy(null)}
                    aria-label={`Show phenotypes of all anatomy, not just ${anatomy.label}`}
                    title="Clear"
                  >
                    ✕
                  </SearchClear>
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
            {(!isBrowsing || anatomy) && (
              <PickerSearch
                value={search.query}
                onChange={search.setQuery}
                label="Search for a phenotype"
                placeholder={
                  isBrowsing && anatomy
                    ? `Search phenotypes of ${anatomy.label}`
                    : "Search all zebrafish phenotypes"
                }
              />
            )}
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
              <Empty>
                {!query && !(isBrowsing && anatomy) && (
                  <EmptyTitle>
                    {isBrowsing ? "No anatomy selected" : "Start typing to search"}
                  </EmptyTitle>
                )}
                <EmptyText>{emptyMessage}</EmptyText>
              </Empty>
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
    </>
  );
};

export default PhenotypePicker;
