import { useCallback, useState } from "react";
import {
  AddButton,
  AddRow,
  AddRowInline,
  EntryBody,
  EntryCard,
  EntryHead,
  EntryMeta,
  EntryRemove,
  EntryTitle,
  FieldGrid,
  EntryCaret,
  GroupSummaryText,
  GroupToggle,
  RadioGroup,
  RadioLabel,
  SelectInput,
  TextArea,
  TextInput,
} from "@/styles/elements";
import { useFieldArray, useFormContext } from "react-hook-form";
import Field from "../Field";
import { emptyControl, emptyImage, type Submission } from "../submission";
import { ImageUpload, Measure } from "../imageEntry";
import { MEASURES } from "../measures";

const TYPES = ["Negative control / untreated", "Vehicle control"];

const VEHICLES = [
  "Dimethylformamide (DMF)",
  "Dimethyl sulfoxide (DMSO)",
  "Embryonic media (EM/E3)",
  "Ethanol",
  "Methylcellulose",
];

const REARING = ["Standard", "Not standard"];

/** One image attached to a control, with its own metadata. */
const ControlImage = ({
  n,
  control: c,
  index,
  onRemove,
}: {
  n: number;
  control: number;
  index: number;
  onRemove: () => void;
}) => {
  const { register } = useFormContext<Submission>();
  const at = `controls.${c}.images.${index}` as const;

  return (
  <EntryCard>
    <EntryHead>
      <EntryTitle>Image {n}</EntryTitle>
      <EntryRemove type="button" onClick={onRemove}>
        Remove
      </EntryRemove>
    </EntryHead>

    <EntryBody>
      <ImageUpload required={false} name={`${at}.file`} />
      <EntryMeta>
        {MEASURES.map(({ field, unitField, ...measure }) => (
          <Measure
            key={measure.label}
            {...measure}
            name={`${at}.${field}` as const}
            unitName={`${at}.${unitField}` as const}
          />
        ))}
        <Field label="Microscope information">
          {(id) => (
            <TextInput
              id={id}
              placeholder="Enter text"
              {...register(`${at}.microscope`)}
            />
          )}
        </Field>
      </EntryMeta>
    </EntryBody>
  </EntryCard>
  );
};

/** What this control was, and what it looked like. */
const Control = ({
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

  const { register, control, watch } = useFormContext<Submission>();
  const at = `controls.${index}` as const;
  const [type, vehicle, strain, rearing] = watch([
    `${at}.type`,
    `${at}.vehicle`,
    `${at}.strain`,
    `${at}.rearing`,
  ]);
  const images = useFieldArray({ control, name: `${at}.images` });

  // Only what has been filled in: a control with nothing entered says nothing.
  const summary = [
    type === "Vehicle control" ? vehicle : "",
    strain,
    images.fields.length ? `${images.fields.length} images` : "No images",
  ].filter(Boolean);

  return (
    <EntryCard>
      <EntryHead>
        <GroupToggle type="button" onClick={toggle} aria-expanded={isOpen}>
          <EntryCaret aria-hidden="true" isOpen={isOpen}>
            ▶
          </EntryCaret>
          Control {n}
        </GroupToggle>
        {type && <GroupSummaryText>{type}</GroupSummaryText>}
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
              <Field wide label="Control type" labels="value">
                {(_id, labelId) => (
                  <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                    {TYPES.map((option) => (
                      <RadioLabel key={option}>
                        <input
                          type="radio"
                          value={option}
                          {...register(`${at}.type`)}
                        />
                        {option}
                      </RadioLabel>
                    ))}
                  </RadioGroup>
                )}
              </Field>

            <Field label="Vehicle used">
              {(id) => (
                <SelectInput id={id} {...register(`${at}.vehicle`)}>
                  <option value="">Select vehicle used</option>
                  {VEHICLES.map((option) => (
                    <option key={option}>{option}</option>
                  ))}
                </SelectInput>
              )}
            </Field>

            <Field label="Strain / background">
              {(id) => (
                <TextInput
                  id={id}
                  placeholder="e.g. AB/TL"
                  {...register(`${at}.strain`)}
                />
              )}
            </Field>

            <Field label="Line description">
              {(id) => <TextInput id={id} {...register(`${at}.lineDescription`)} />}
            </Field>

              <Field wide label="Rearing conditions" labels="value">
                {(_id, labelId) => (
                  <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                    {REARING.map((option) => (
                      <RadioLabel key={option}>
                        <input
                          type="radio"
                          value={option}
                          {...register(`${at}.rearing`)}
                        />
                        {option}
                      </RadioLabel>
                    ))}
                  </RadioGroup>
                )}
              </Field>

              {rearing === "Not standard" && (
                <Field wide label="Describe">
                  {(id) => (
                    <TextArea id={id} rows={3} {...register(`${at}.rearingComment`)} />
                  )}
                </Field>
              )}

              <Field wide label="Phenotype description">
                {(id) => (
                  <TextArea
                    id={id}
                    rows={3}
                    {...register(`${at}.phenotypeDescription`)}
                  />
                )}
              </Field>

              <Field wide label="Notes">
                {(id) => <TextArea id={id} rows={3} {...register(`${at}.notes`)} />}
              </Field>
          </FieldGrid>

          <EntryTitle>Control images (optional)</EntryTitle>

          {images.fields.map((field, i) => (
            <ControlImage
              key={field.id}
              n={i + 1}
              control={index}
              index={i}
              onRemove={() => images.remove(i)}
            />
          ))}

          <AddRowInline>
            <AddButton type="button" onClick={() => images.append(emptyImage())}>
              + Add control image
            </AddButton>
          </AddRowInline>
        </>
      )}
    </EntryCard>
  );
};

/** The controls this submission was measured against. */
const ControlSection = () => {
  const { control } = useFormContext<Submission>();
  const { fields, append, remove } = useFieldArray({ control, name: "controls" });

  return (
    <>
      {fields.map((field, i) => (
        <Control
          key={field.id}
          n={i + 1}
          index={i}
          onRemove={fields.length > 1 ? () => remove(i) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={() => append(emptyControl())}>
          + Add another control
        </AddButton>
      </AddRow>
    </>
  );
};

export default ControlSection;
