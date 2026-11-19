import { lazy, Suspense, useState } from "react";
import type { OBOGraphNode } from "frogpot";
import Modal from "@/components/Modal";
import { ChevronIcon, SearchIcon } from "@/components/icons";
import {
  AddButton,
  AddRow,
  EntryCard,
  EntryHead,
  EntryRemove,
  EntryTitle,
  FieldGrid,
  FieldNote,
  MeasureGrid,
  MeasureInput,
  MeasureSuffix,
  RadioGroup,
  RadioLabel,
  SearchClear,
  SearchHint,
  ModalBanded,
  ModalBody,
  ModalFoot,
  ModalHead,
  ModalText,
  ModalTitle,
  SubstanceCard,
  SubstanceChange,
  SubstanceChosen,
  SubstanceId,
  SubstanceName,
  SubstanceNames,
  PhenotypeChoose,
  TextInput,
} from "@/styles/elements";
import { useFieldArray, useFormContext } from "react-hook-form";
import { curieOf } from "../curie";
import Field from "../Field";
import type { Body } from "@/schema/bodies";
import { asNumber } from "../quantity";
import StageField from "../StageField";
import { PHENOTYPE_INFO } from "../explanations";

// Loaded the first time the picker opens, like the ontologies it shows: it
// brings frogpot and its search indexes, which no other page needs.
const PhenotypePicker = lazy(() => import("../PhenotypePicker"));

type Values = Body<"PhenotypeObservationSet">;

const SEVERITIES = [
  { value: "mild", label: "Mild" },
  { value: "moderate", label: "Moderate" },
  { value: "severe", label: "Severe" },
] as const;

/**
 * A phenotype seen in the exposed fish, and how strongly. Always open: it
 * sits inside an observation, which is the card that folds.
 */
const Phenotype = ({
  n,
  index,
  onRemove,
}: {
  n: number;
  index: number;
  onRemove?: () => void;
}) => {
  const { register, setValue, watch } = useFormContext<Values>();
  const at = `phenotype.${index}` as const;
  const term = watch(`${at}.phenotype_term_id`);
  const phenotypeId = term?.term_uri;
  const phenotype = term?.term_label ?? phenotypeId;

  // The picker's choice is held here until confirmed, so cancelling it
  // leaves the field as it was.
  const [isPicking, setIsPicking] = useState(false);
  const [pending, setPending] = useState<OBOGraphNode | null>(null);
  const closePicker = () => {
    setIsPicking(false);
    setPending(null);
  };
  const confirmPick = () => {
    if (pending) {
      // The term's id is what is stored; its label goes with it to be shown.
      setValue(
        `${at}.phenotype_term_id`,
        { term_uri: curieOf(pending.uri), term_label: pending.label },
        { shouldDirty: true, shouldValidate: true },
      );
    }
    closePicker();
  };

  return (
    <EntryCard>
      <EntryHead>
        <EntryTitle>Phenotype {n}</EntryTitle>
        {onRemove && (
          <EntryRemove type="button" onClick={onRemove}>
            Remove
          </EntryRemove>
        )}
      </EntryHead>

          <FieldGrid>
            <Field
              wide
              label="Observed phenotype"
              labels="value"
              info={<p>{PHENOTYPE_INFO}</p>}
            >
              {(_id, labelId) => (
                <>
                  {phenotypeId ? (
                    <SubstanceCard role="group" aria-labelledby={labelId}>
                      <SubstanceChosen>
                        <SubstanceNames>
                          <SubstanceName>{phenotype}</SubstanceName>
                          <SubstanceId>{phenotypeId}</SubstanceId>
                        </SubstanceNames>
                        <SubstanceChange
                          type="button"
                          onClick={() => setIsPicking(true)}
                        >
                          Change
                        </SubstanceChange>
                      </SubstanceChosen>
                    </SubstanceCard>
                  ) : (
                    <PhenotypeChoose
                      type="button"
                      aria-describedby={labelId}
                      onClick={() => setIsPicking(true)}
                    >
                      <SearchIcon />
                      Choose a phenotype
                      <ChevronIcon />
                    </PhenotypeChoose>
                  )}
                  <FieldNote>
                    Term not represented correctly? Request a new synonym — TBD
                  </FieldNote>
                </>
              )}
            </Field>

            <MeasureGrid>
              <StageField
                label="Fish stage at observation"
                name={`${at}.stage`}
                required
              />

              <Field label="Prevalence" name={`${at}.prevalence`}>
                {(id, _labelId, errorProps) => (
                  <MeasureInput>
                    <TextInput
                      id={id}
                      inputMode="decimal"
                      placeholder="e.g. 80"
                      {...errorProps}
                      {...register(`${at}.prevalence`, { setValueAs: asNumber })}
                    />
                    <MeasureSuffix>%</MeasureSuffix>
                  </MeasureInput>
                )}
              </Field>
            </MeasureGrid>

            <Field wide label="Severity" labels="value">
              {(_id, labelId) => (
                <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                  {SEVERITIES.map((option) => (
                    <RadioLabel key={option.value}>
                      <input
                        type="radio"
                        value={option.value}
                        {...register(`${at}.severity`)}
                      />
                      {option.label}
                    </RadioLabel>
                  ))}
                </RadioGroup>
              )}
            </Field>
          </FieldGrid>

      <Modal
        open={isPicking}
        title="Choose a phenotype"
        onClose={closePicker}
        isLarge
      >
        <ModalBanded>
          <ModalHead>
            <ModalTitle>Choose a phenotype</ModalTitle>
            <ModalText>
              Search for a phenotype, or choose an anatomical entity to list
              the phenotypes associated with it.
            </ModalText>
            <SearchClear type="button" onClick={closePicker} aria-label="Close">
              ✕
            </SearchClear>
          </ModalHead>
          <ModalBody>
            <Suspense fallback={<SearchHint role="status">Loading…</SearchHint>}>
              <PhenotypePicker onSelectNode={setPending} />
            </Suspense>
          </ModalBody>
          <ModalFoot>
            <button className="btn btn--secondary" type="button" onClick={closePicker}>
              Cancel
            </button>
            <button
              className="btn btn--primary"
              type="button"
              onClick={confirmPick}
              disabled={!pending}
            >
              Use this phenotype
            </button>
          </ModalFoot>
        </ModalBanded>
      </Modal>
    </EntryCard>
  );
};

/** The phenotypes seen at one observation, in the order they were entered. */
const PhenotypeFields = () => {
  const { control } = useFormContext<Values>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: "phenotype",
  });
  return (
    <>
      {fields.map((field, i) => (
        <Phenotype
          key={field.id}
          n={i + 1}
          index={i}
          onRemove={fields.length > 1 ? () => remove(i) : undefined}
        />
      ))}

      <AddRow>
        {/* A row with nothing filled in is not saved. */}
        <AddButton type="button" onClick={() => append({})}>
          + Add another phenotype
        </AddButton>
      </AddRow>
    </>
  );
};

export default PhenotypeFields;
