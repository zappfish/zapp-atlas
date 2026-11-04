import { lazy, Suspense, useCallback, useState } from "react";
import type { OBOGraphNode } from "frogpot";
import Modal from "@/components/Modal";
import { ChevronIcon, SearchIcon } from "@/components/icons";
import {
  AddButton,
  AddRow,
  EntryCaret,
  EntryCard,
  EntryHead,
  EntryRemove,
  FieldGrid,
  FieldNote,
  MeasureGrid,
  GroupSummaryText,
  GroupToggle,
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
import { emptyObservation, type Submission } from "../submission";
import { PERCENT } from "../validation";
import StageField from "../StageField";
import { PHENOTYPE_INFO } from "../explanations";

// Loaded the first time the picker opens, like the ontologies it shows: it
// brings frogpot and its search indexes, which no other page needs.
const PhenotypePicker = lazy(() => import("../PhenotypePicker"));

const SEVERITIES = ["Mild", "Moderate", "Severe"];

/** A phenotype seen in the exposed fish, and how strongly. */
const Observation = ({
  n,
  index,
  defaultOpen,
  onRemove,
}: {
  n: number;
  index: number;
  defaultOpen: boolean;
  onRemove?: () => void;
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const toggle = useCallback(() => setIsOpen((was) => !was), []);

  const { register, setValue, watch } = useFormContext<Submission>();
  const at = `observations.${index}` as const;
  const [phenotype, phenotypeId, severity] = watch([
    `${at}.phenotype`,
    `${at}.phenotypeId`,
    `${at}.severity`,
  ]);

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
      const curie = curieOf(pending.uri);
      setValue(`${at}.phenotype`, pending.label ?? curie, { shouldDirty: true });
      setValue(`${at}.phenotypeId`, curie, { shouldDirty: true });
    }
    closePicker();
  };

  // Only what has been filled in: an empty observation says nothing.
  const summary = [severity].filter(Boolean);

  return (
    <EntryCard>
      <EntryHead>
        <GroupToggle type="button" onClick={toggle} aria-expanded={isOpen}>
          <EntryCaret aria-hidden="true" isOpen={isOpen}>
            ▶
          </EntryCaret>
          Observation {n}
        </GroupToggle>
        {phenotype && <GroupSummaryText>{phenotype}</GroupSummaryText>}
        {onRemove && (
          <EntryRemove type="button" onClick={onRemove}>
            Remove
          </EntryRemove>
        )}
      </EntryHead>

      {!isOpen && summary.length > 0 && (
        <GroupSummaryText>{summary.join(" • ")}</GroupSummaryText>
      )}

      {isOpen && (
        <>
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
                unitName={`${at}.stageUnit`}
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
                      {...register(`${at}.prevalence`, PERCENT)}
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
                    <RadioLabel key={option}>
                      <input
                        type="radio"
                        value={option}
                        {...register(`${at}.severity`)}
                      />
                      {option}
                    </RadioLabel>
                  ))}
                </RadioGroup>
              )}
            </Field>
          </FieldGrid>
        </>
      )}

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

/** The phenotypes this submission reports. */
const PhenotypeSection = () => {
  const { control } = useFormContext<Submission>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: "observations",
  });
  // Those already there on load start collapsed after the first; one added
  // with the button opens, since it is about to be filled in.
  const [initialIds] = useState(() => new Set(fields.map((f) => f.id)));

  return (
    <>
      {fields.map((field, i) => (
        <Observation
          key={field.id}
          n={i + 1}
          index={i}
          defaultOpen={i === 0 || !initialIds.has(field.id)}
          onRemove={fields.length > 1 ? () => remove(i) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={() => append(emptyObservation())}>
          + Add another observation
        </AddButton>
      </AddRow>
    </>
  );
};

export default PhenotypeSection;
