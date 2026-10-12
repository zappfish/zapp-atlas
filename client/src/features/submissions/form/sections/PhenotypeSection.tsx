import { useCallback, useState } from "react";
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
  SelectInput,
  TextInput,
} from "@/styles/elements";
import { useFieldArray, useFormContext } from "react-hook-form";
import Field from "../Field";
import { emptyObservation, type Submission } from "../submission";

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

  const { register, watch } = useFormContext<Submission>();
  const at = `observations.${index}` as const;
  const [phenotype, severity] = watch([`${at}.phenotype`, `${at}.severity`]);

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
                {(id) => <TextInput id={id} placeholder="e.g. 96" {...register(`${at}.stage`)} />}
              </Field>
              <Field label="Unit">
                {(id) => (
                  <SelectInput id={id} {...register(`${at}.stageUnit`)}>
                    {STAGE_UNITS.map((unit) => (
                      <option key={unit}>{unit}</option>
                    ))}
                  </SelectInput>
                )}
              </Field>

            <Field label="Observed phenotype">
              {(id) => (
                <>
                  <TextInput
                    id={id}
                    placeholder="Phenotype term"
                    {...register(`${at}.phenotype`)}
                  />
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
