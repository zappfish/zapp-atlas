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
  SearchOption,
  SearchQuery,
  SearchType,
  StageButton,
  TermSearch,
} from "@/styles/elements";

export interface Staged {
  chebiId: string;
  name: string;
}

type Mode = "name" | "id";

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
 * cannot be chosen — only the identifier is stored, so there would be nothing
 * to save.
 *
 * Omitting `staged` and `limit` gives the one-at-a-time form: `onPick` fires on
 * selection, with no staging list and no button.
 */
const ChemicalPicker = ({
  staged = [],
  limit,
  alreadyIn,
  isDisabled = false,
  onPick,
}: {
  staged?: Staged[];
  /** Absent when one chemical is chosen rather than several staged. */
  limit?: number;
  /** Already held, so it cannot be chosen twice. */
  alreadyIn?: Set<string>;
  /** Held while the caller is saving what has been staged. */
  isDisabled?: boolean;
  onPick: (chemical: Staged) => void;
}) => {
  const [mode, setMode] = useState<Mode>("name");
  const [idType, setIdType] = useState<string>(ID_TYPES[0].id);
  const [query, setQuery] = useState("");
  const [chosen, setChosen] = useState<Staged | null>(null);
  const listId = useId();
  const settled = useDebounced(query);

  const byName = useChemicalSearch(mode === "name" ? settled : "");
  const byId = useChemicalByCurie(
    mode === "id" && settled.trim() ? toCurie(idType, settled) : null,
  );
  const suggestions = (mode === "name" ? byName.data : byId.data) ?? [];

  const isFull = limit !== undefined && staged.length >= limit;
  const source = idTypeOf(idType)?.label ?? idType;
  const isSearching = mode === "name" ? byName.isFetching : byId.isFetching;
  const didSearch =
    mode === "name"
      ? settled.trim().length >= MIN_SEARCH_LENGTH
      : settled.trim() !== "";
  const foundNothing = didSearch && !isSearching && suggestions.length === 0;

  const isStaging = limit !== undefined;

  const choose = (suggestion: Suggestion) => {
    const chebiId = idOf(suggestion);
    if (!chebiId) return;
    const picked = { chebiId, name: suggestion.name };
    setQuery("");
    if (isStaging) {
      setChosen(picked);
      return;
    }
    onPick(picked);
  };

  const reset = () => {
    setChosen(null);
    setQuery("");
  };

  const stage = () => {
    if (!chosen) return;
    onPick(chosen);
    reset();
  };

  const switchTo = (next: Mode) => {
    setMode(next);
    reset();
  };

  return (
    <TermSearch>
      <SearchFields>
        <SearchType>
          <ModalLabel>Search by</ModalLabel>
          <ModalSelect
            disabled={isDisabled}
            value={mode}
            onChange={(e) => switchTo(e.target.value as Mode)}
          >
            <option value="name">Chemical name</option>
            <option value="id">Identifier</option>
          </ModalSelect>
        </SearchType>

        {mode === "id" && (
          <SearchType>
            <ModalLabel>Identifier type</ModalLabel>
            <ModalSelect
              disabled={isDisabled}
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
            {mode === "name" ? "Chemical name" : `${source} value`}
          </ModalLabel>
          <SearchBox>
            <SearchIconSlot aria-hidden="true">
              <SearchIcon />
            </SearchIconSlot>
            <SearchInput
              disabled={isDisabled}
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
                disabled={isDisabled}
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
                    ((alreadyIn?.has(chebiId) ?? false) ||
                      staged.some((each) => each.chebiId === chebiId));

                  return (
                    <li key={suggestion.name}>
                      <SearchOption
                        type="button"
                        disabled={chebiId === null || added || isFull || isDisabled}
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

      {isStaging && chosen && (
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
        {isStaging && (
          <StageButton type="button" onClick={stage} disabled={!chosen || isFull || isDisabled}>
            + Add chemical
          </StageButton>
        )}
      </SearchFooter>
    </TermSearch>
  );
};

export default ChemicalPicker;
