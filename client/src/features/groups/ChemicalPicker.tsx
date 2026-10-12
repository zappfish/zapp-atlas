import { useId, useState } from "react";
import {
  MIN_SEARCH_LENGTH,
  useChemical,
  useChemicalByCurie,
  useChemicalSearch,
} from "@/api/hooks";
import { useDebounced } from "@/useDebounced";
import {
  ID_TYPES,
  idTypeOf,
  toCurie,
  type Suggestion,
} from "@/api/chemicals";
import { FlaskIcon, SearchIcon } from "@/components/icons";
import {
  ModalLabel,
  ModalSelect,
  OptionId,
  OptionName,
  OptionNote,
  OptionText,
  Preview,
  PreviewDescription,
  PreviewIcon,
  PreviewId,
  PreviewName,
  SearchBox,
  SearchClear,
  SearchFields,
  SearchFooter,
  SearchHint,
  SearchIconSlot,
  SearchInput,
  SearchList,
  SearchMiss,
  SearchMode,
  SearchModes,
  SearchOption,
  SearchQuery,
  SearchSublabel,
  SearchType,
  StageButton,
  TermSearch,
} from "@/styles/elements";

export interface Staged {
  chebiId: string;
  name: string;
}

type Mode = "name" | "id";

const MODES: Mode[] = ["name", "id"];

/** null when the suggestion has no ChEBI id. */
const idOf = (suggestion: Suggestion) => suggestion.chebi_ids[0] ?? null;

/** The chosen chemical, pending staging. */
const ChemicalCard = ({ chebiId, name }: { chebiId: string; name: string }) => {
  const { data, isPending } = useChemical(chebiId);

  return (
    <Preview>
      <PreviewIcon aria-hidden="true">
        <FlaskIcon />
      </PreviewIcon>
      <div>
        <PreviewName>{data?.label ?? name}</PreviewName>
        <PreviewId>{data?.primary_id ?? chebiId}</PreviewId>
        {(isPending || data?.description) && (
          <PreviewDescription>
            {isPending ? "Looking up…" : data?.description}
          </PreviewDescription>
        )}
      </div>
    </Preview>
  );
};

/**
 * Search by name or by an identifier from any source. A result with no ChEBI id
 * cannot be staged — the cabinet stores one, so there would be nothing to save.
 */
const ChemicalPicker = ({
  staged,
  limit,
  alreadyIn,
  onStage,
}: {
  staged: Staged[];
  limit: number;
  /** Already in the cabinet, so it cannot be added twice. */
  alreadyIn: Set<string>;
  onStage: (chemical: Staged) => void;
}) => {
  const [mode, setMode] = useState<Mode>("name");
  const [query, setQuery] = useState("");
  const [idType, setIdType] = useState<string>(ID_TYPES[0].id);
  const [chosen, setChosen] = useState<Staged | null>(null);
  const listId = useId();
  const settled = useDebounced(query);

  const byName = useChemicalSearch(mode === "name" ? settled : "");
  const byId = useChemicalByCurie(
    mode === "id" && settled.trim() ? toCurie(idType, settled) : null,
  );
  const suggestions = (mode === "name" ? byName.data : byId.data) ?? [];

  const isFull = staged.length >= limit;
  const source = idTypeOf(idType)?.label ?? idType;
  const isSearching = mode === "name" ? byName.isFetching : byId.isFetching;
  const didSearch =
    mode === "name"
      ? settled.trim().length >= MIN_SEARCH_LENGTH
      : settled.trim() !== "";
  const foundNothing = didSearch && !isSearching && suggestions.length === 0;

  const choose = (suggestion: Suggestion) => {
    const chebiId = idOf(suggestion);
    if (!chebiId) return;
    setChosen({ chebiId, name: suggestion.name });
    setQuery("");
  };

  const reset = () => {
    setChosen(null);
    setQuery("");
  };

  const stage = () => {
    if (!chosen) return;
    onStage(chosen);
    reset();
  };

  const switchTo = (next: Mode) => {
    setMode(next);
    reset();
  };

  return (
    <TermSearch>
      <SearchModes role="tablist">
        {MODES.map((each) => (
          <SearchMode
            key={each}
            isActive={mode === each}
            type="button"
            role="tab"
            aria-selected={mode === each}
            onClick={() => switchTo(each)}
          >
            {each === "name" ? "Search by name" : "Search by ID"}
          </SearchMode>
        ))}
      </SearchModes>

      <SearchFields>
        {mode === "id" && (
          <SearchType>
            <ModalLabel>ID type</ModalLabel>
            <SearchSublabel>Choose the source.</SearchSublabel>
            <ModalSelect
              value={idType}
              onChange={(e) => {
                setIdType(e.target.value);
                reset();
              }}
            >
              {ID_TYPES.map((each) => (
                <option key={each.id} value={each.id}>
                  {each.label}
                </option>
              ))}
            </ModalSelect>
          </SearchType>
        )}

        <SearchQuery>
          <ModalLabel>
            {mode === "name" ? "Chemical name" : "Identifier"}
          </ModalLabel>
          <SearchSublabel>
            {mode === "name"
              ? "Enter a common or scientific chemical name."
              : "Enter the identifier, with or without its prefix."}
          </SearchSublabel>
          <SearchBox>
            <SearchIconSlot aria-hidden="true">
              <SearchIcon />
            </SearchIconSlot>
            <SearchInput
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setChosen(null);
              }}
              autoFocus
              role="combobox"
              aria-expanded={suggestions.length > 0}
              aria-controls={listId}
              aria-autocomplete="list"
              placeholder={
                mode === "name"
                  ? "Start typing a chemical name…"
                  : `e.g. ${idTypeOf(idType)?.example ?? ""}`
              }
            />
            {query && (
              <SearchClear
                type="button"
                onClick={reset}
                aria-label="Clear the search"
              >
                ✕
              </SearchClear>
            )}

            {suggestions.length > 0 && (
              <SearchList id={listId} role="listbox">
                {suggestions.map((suggestion) => {
                  const chebiId = idOf(suggestion);
                  const added =
                    chebiId !== null &&
                    (alreadyIn.has(chebiId) ||
                      staged.some((each) => each.chebiId === chebiId));

                  return (
                    <li key={suggestion.name}>
                      <SearchOption
                        type="button"
                        disabled={chebiId === null || added || isFull}
                        onClick={() => choose(suggestion)}
                      >
                        <OptionText>
                          <OptionName>{suggestion.name}</OptionName>
                          <OptionId>{chebiId ?? "No ChEBI ID"}</OptionId>
                        </OptionText>
                        {added && <OptionNote>Already added</OptionNote>}
                      </SearchOption>
                    </li>
                  );
                })}
              </SearchList>
            )}
          </SearchBox>
        </SearchQuery>
      </SearchFields>

      {chosen && (
        <ChemicalCard chebiId={chosen.chebiId} name={chosen.name} />
      )}

      <SearchFooter>
        {foundNothing ? (
          <SearchMiss role="status">
            {mode === "name"
              ? `No chemical found matching "${settled.trim()}".`
              : `No chemical found with that ${source} identifier.`}
          </SearchMiss>
        ) : (
          !chosen && (
            <SearchHint>
              {mode === "name"
                ? "Select a result to review its ID and description."
                : `Enter a ${source} identifier to find a chemical.`}
            </SearchHint>
          )
        )}
        <StageButton type="button" onClick={stage} disabled={!chosen || isFull}>
          + Add chemical
        </StageButton>
      </SearchFooter>
    </TermSearch>
  );
};

export default ChemicalPicker;
