import { useId, useState } from "react";
import { MIN_SEARCH_LENGTH, useAlleleSearch } from "@/api/hooks";
import type { ZfinAllele } from "@/api/types";
import { SearchIcon } from "@/components/icons";
import { alleleDescription, mutagenGloss } from "@/fish";
import { useDebounced } from "@/useDebounced";
import {
  ModalLabel,
  OptionId,
  OptionName,
  OptionNote,
  OptionText,
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
  TermSearch,
} from "@/styles/elements";

/**
 * One box that finds a ZFIN allele by its symbol, the gene it affects, or a
 * fragment of its construct's name. Picking a hit hands it to the caller and
 * clears the box, ready for the next one.
 */
const AlleleSearch = ({
  alreadyIn,
  isDisabled = false,
  onPick,
}: {
  /** Allele ids already on the fish, so one cannot be added twice. */
  alreadyIn: Set<string>;
  isDisabled?: boolean;
  onPick: (allele: ZfinAllele) => void;
}) => {
  const [query, setQuery] = useState("");
  const listId = useId();
  const settled = useDebounced(query);
  const search = useAlleleSearch(settled);
  const hits = search.data?.results ?? [];
  const didSearch = settled.trim().length >= MIN_SEARCH_LENGTH;
  const foundNothing = didSearch && !search.isFetching && hits.length === 0;

  const choose = (allele: ZfinAllele) => {
    setQuery("");
    onPick(allele);
  };

  return (
    <TermSearch>
      <SearchFields>
        <SearchQuery>
          <ModalLabel>Alleles</ModalLabel>
          <SearchBox>
            <SearchIconSlot aria-hidden="true">
              <SearchIcon />
            </SearchIconSlot>
            <SearchInput
              disabled={isDisabled}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              role="combobox"
              aria-expanded={hits.length > 0}
              aria-controls={listId}
              aria-autocomplete="list"
              placeholder="Allele (fh111), gene (fgf8a) or construct (mpeg1:YFP)"
            />
            {query && (
              <SearchClear
                type="button"
                onClick={() => setQuery("")}
                aria-label="Clear the search"
                disabled={isDisabled}
              >
                ✕
              </SearchClear>
            )}

            {hits.length > 0 && (
              <SearchList id={listId} role="listbox">
                {hits.map((allele) => {
                  const added = alreadyIn.has(allele.allele_id);
                  return (
                    <li key={allele.allele_id}>
                      <SearchOption
                        type="button"
                        disabled={added || isDisabled}
                        onClick={() => choose(allele)}
                      >
                        <OptionText>
                          <OptionName>
                            {allele.symbol}
                            {allele.is_transgenic && " · Tg"}
                          </OptionName>
                          <OptionId>
                            {alleleDescription(allele)}
                            {allele.mutagen && ` · made with ${mutagenGloss(allele.mutagen)}`}
                          </OptionId>
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

      <SearchFooter>
        {foundNothing ? (
          <SearchMiss role="status">
            No ZFIN allele matches "{settled.trim()}". If ZFIN does not have the line,
            describe it in the notes.
          </SearchMiss>
        ) : (
          <SearchHint>
            {search.data && search.data.total_matches > hits.length
              ? `Showing ${hits.length} of ${search.data.total_matches} matches; keep typing to narrow.`
              : "Pick an allele to add it; then choose its zygosity."}
          </SearchHint>
        )}
      </SearchFooter>
    </TermSearch>
  );
};

export default AlleleSearch;
