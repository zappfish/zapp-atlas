import {
  EntryCard,
  FieldGrid,
  RadioGroup,
  RadioLabel,
  TextArea,
  TextInput,
} from "@/styles/elements";
import { useFormContext } from "react-hook-form";
import Field from "../Field";
import type { Submission } from "../submission";
import OptionalNotes from "../OptionalNotes";

const REARING = ["Standard", "Non-standard"];

/** The fish the experiment used, and how it was reared. */
const FishSection = () => {
  const { register, watch } = useFormContext<Submission>();
  const rearing = watch("fish.rearing");

  return (
    <EntryCard>
      <FieldGrid>
        <Field label="Select existing fish">
          {(id) => <TextInput
              id={id}
              placeholder="Fish name or ZFIN ID"
              {...register("fish.existing")}
            />}
        </Field>

        <Field label="Strain / line" required>
          {(id) => <TextInput id={id} placeholder="e.g. AB/TL" {...register("fish.strain")} />}
        </Field>

        <Field label="Additional condition">
          {(id) => <TextInput id={id} {...register("fish.additionalCondition")} />}
        </Field>

        {/* After the short fields, so its height strands nothing beside it. */}
        <Field label="Line description">
          {(id) => (
            <TextArea
              id={id}
              rows={1}
              placeholder="For a transgenic or mutant line, or a wild type not listed"
              {...register("fish.lineDescription")}
            />
          )}
        </Field>

          {/* A group of radios has no one control to point `for` at, so the
              label is a span and the group is named by it. */}
          <Field wide label="Fish rearing conditions" labels="value">
            {(_id, labelId) => (
              <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                {REARING.map((option) => (
                  <RadioLabel key={option}>
                    <input
                      type="radio"
                      value={option}
                      {...register("fish.rearing")}
                    />
                    {option}
                  </RadioLabel>
                ))}
              </RadioGroup>
            )}
          </Field>

          {rearing === "Non-standard" && (
            <Field wide label="Describe the conditions" required>
              {(id) => (
                <TextArea id={id} rows={3} {...register("fish.rearingComment")} />
              )}
            </Field>
          )}
      </FieldGrid>

      <OptionalNotes name="fish.notes" />
    </EntryCard>
  );
};

export default FishSection;
