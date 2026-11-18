import type { ReactNode } from "react";
import {
  SubstanceAdd,
  SubstanceBack,
  SubstanceBody,
  SubstanceCard,
  SubstanceChange,
  SubstanceChoices,
  SubstanceChosen,
  SubstanceHead,
  SubstanceIcon,
  SubstanceId,
  SubstanceLead,
  SubstanceName,
  SubstanceNames,
  SubstanceOr,
  SubstanceSaved,
  SubstanceSearch,
  SubstanceTitle,
  SelectInput,
} from "@/styles/elements";

/**
 * The form's panel for picking from the group's stock (the cabinet or the
 * tank) or adding to it. Three views, built from the exposure's chemical
 * panel and its `substance` elements: choosing, searching, and chosen. A
 * section supplies the words, the options and the buttons after "OR".
 */

export interface StockOption {
  value: string;
  label: string;
}

/** Before anything is chosen: the group's stock in a select, or how to add to it. */
export const StockChoices = ({
  title,
  selectLabel,
  placeholder,
  options,
  onPick,
  emptyText,
  whenEmpty,
  alternatives,
  children,
}: {
  title: string;
  /** Names the select for assistive technology; the title is not a label. */
  selectLabel: string;
  placeholder: string;
  options: StockOption[];
  onPick: (value: string) => void;
  /** Shown in place of the select when the stock is empty. */
  emptyText: string;
  /** Beside the empty-state text, e.g. a button that opens the add dialog. */
  whenEmpty?: ReactNode;
  /** The other ways to get one, after "OR". */
  alternatives?: ReactNode;
  /** Dialogs the panel opens, rendered alongside it. */
  children?: ReactNode;
}) => (
  <SubstanceCard>
    <SubstanceBody>
      <SubstanceTitle>{title}</SubstanceTitle>
      <SubstanceChoices>
        {options.length > 0 ? (
          <SelectInput
            defaultValue=""
            aria-label={selectLabel}
            onChange={(e) => {
              if (e.target.value) onPick(e.target.value);
            }}
          >
            <option value="" disabled>
              {placeholder}
            </option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </SelectInput>
        ) : (
          <>
            <SubstanceLead>{emptyText}</SubstanceLead>
            {whenEmpty}
          </>
        )}

        {alternatives && (
          <>
            <SubstanceOr>OR</SubstanceOr>
            {alternatives}
          </>
        )}
      </SubstanceChoices>
    </SubstanceBody>

    {children}
  </SubstanceCard>
);

/** What was chosen, in place of the ways of choosing it. */
export const StockChosen = ({
  icon,
  name,
  detail,
  actions,
  onChange,
  isDisabled = false,
}: {
  icon?: ReactNode;
  name: string;
  /** A second line: an identifier, a description. */
  detail?: string;
  /** Between the names and Change, e.g. "Add to cabinet". */
  actions?: ReactNode;
  onChange: () => void;
  isDisabled?: boolean;
}) => (
  <SubstanceCard>
    <SubstanceChosen>
      {icon && <SubstanceIcon aria-hidden="true">{icon}</SubstanceIcon>}
      <SubstanceNames>
        <SubstanceName>{name}</SubstanceName>
        {detail && <SubstanceId>{detail}</SubstanceId>}
      </SubstanceNames>
      {actions}
      <SubstanceChange type="button" onClick={onChange} disabled={isDisabled}>
        Change
      </SubstanceChange>
    </SubstanceChosen>
  </SubstanceCard>
);

/** A search in the panel's place, with a way back to the stock. */
export const StockSearch = ({
  title,
  lead,
  backLabel,
  onBack,
  children,
}: {
  title: string;
  lead: string;
  backLabel: string;
  onBack: () => void;
  children: ReactNode;
}) => (
  <SubstanceCard>
    <SubstanceHead>
      <div>
        <SubstanceTitle>{title}</SubstanceTitle>
        <SubstanceLead>{lead}</SubstanceLead>
      </div>
      <SubstanceBack type="button" onClick={onBack}>
        {backLabel}
      </SubstanceBack>
    </SubstanceHead>
    <SubstanceBody>{children}</SubstanceBody>
  </SubstanceCard>
);

/* The buttons and notes a section puts in the slots above, so it imports
   nothing from the element module itself. */
export const StockAdd = SubstanceAdd;
export const StockSearchButton = SubstanceSearch;
export const StockSaved = SubstanceSaved;
