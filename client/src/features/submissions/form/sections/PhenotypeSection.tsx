import { lazy, Suspense, useCallback, useState } from "react";
import type { OBOGraphNode } from "frogpot";
import Modal from "@/components/Modal";
import {
  AddButton,
  AddRow,
  EntryCaret,
  EntryCard,
  EntryHead,
  EntryRemove,
  FieldNote,
  FieldGrid,
  GroupSummaryText,
  GroupToggle,
  MeasureInput,
  MeasureSuffix,
  RadioGroup,
  RadioLabel,
  SearchClear,
  SearchHint,
  MeasureRow,
  ModalBanded,
  ModalBody,
  ModalFoot,
  ModalHead,
  ModalText,
  ModalTitle,
  ShortSelect,
  SubstanceCard,
  SubstanceChange,
  SubstanceChosen,
  SubstanceId,
  SubstanceName,
  SubstanceNames,
  TextInput,
} from "@/styles/elements";
import { useFieldArray, useFormContext } from "react-hook-form";
import { curieOf } from "../curie";
import Field from "../Field";
import { emptyObservation, type Submission } from "../submission";

// Loaded the first time the picker opens, like the ontologies it shows: it
// brings frogpot and its search indexes, which no other page needs.
const PhenotypePicker = lazy(() => import("../PhenotypePicker"));

const STAGE_UNITS = ["hpf", "dpf", "month"];
const SEVERITIES = ["Mild", "Moderate", "Severe"];

/** A phenotype seen in the exposed fish, and how strongly. */
const Observation = ({
  n,
  index,
  onRemove,
}: {
  n: number;
  index: number;
  onRemove?: () => void;
}) => {
  const [isOpen, setIsOpen] = useState(n === 1);
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
            <Field label="Fish stage at phenotype observation">
              {(id) => (
                <MeasureRow>
                  <TextInput
                    id={id}
                    placeholder="e.g. 96"
                    {...register(`${at}.stage`)}
                  />
                  <ShortSelect
                    aria-label="Fish stage unit"
                    {...register(`${at}.stageUnit`)}
                  >
                    {STAGE_UNITS.map((unit) => (
                      <option key={unit}>{unit}</option>
                    ))}
                  </ShortSelect>
                </MeasureRow>
              )}
            </Field>

            <Field
              label="Observed phenotype"
              labels={phenotypeId ? "value" : "control"}
            >
              {(id, labelId) => (
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
                    <MeasureRow>
                      <TextInput
                        id={id}
                        readOnly
                        placeholder="No phenotype chosen"
                        {...register(`${at}.phenotype`)}
                      />
                      <button
                        className="btn btn--secondary"
                        type="button"
                        onClick={() => setIsPicking(true)}
                      >
                        Choose
                      </button>
                    </MeasureRow>
                  )}
                  <FieldNote>
                    Term not represented correctly? Request a new synonym — TBD
                  </FieldNote>
                </>
              )}
            </Field>

            <Field label="Prevalence">
              {(id) => (
                <MeasureInput>
                  <TextInput
                    id={id}
                    placeholder="e.g. 80"
                    {...register(`${at}.prevalence`)}
                  />
                  <MeasureSuffix>%</MeasureSuffix>
                </MeasureInput>
              )}
            </Field>

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

  return (
    <>
      {fields.map((field, i) => (
        <Observation
          key={field.id}
          n={i + 1}
          index={i}
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
