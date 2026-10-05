import { useId, useState } from "react";
import {
  EntryCard,
  FieldGrid,
  RadioGroup,
  RadioLabel,
  TextArea,
  TextInput,
} from "@/styles/elements";
import Field from "../Field";
import OptionalNotes from "../OptionalNotes";

const REARING = ["Standard", "Non-standard"] as const;
type Rearing = (typeof REARING)[number];

/** The fish the experiment used, and how it was reared. */
const FishSection = () => {
  const [rearing, setRearing] = useState<Rearing>("Standard");
  const rearingName = useId();

  return (
    <EntryCard>
      <FieldGrid>
        <Field label="Select existing fish">
          {(id) => <TextInput id={id} placeholder="Fish name or ZFIN ID" />}
        </Field>

        <Field label="Strain / line" required>
          {(id) => <TextInput id={id} placeholder="e.g. AB/TL" />}
        </Field>

        <Field label="Additional condition">{(id) => <TextInput id={id} />}</Field>

        {/* After the short fields, so its height strands nothing beside it. */}
        <Field label="Line description">
          {(id) => (
            <TextArea
              id={id}
              rows={1}
              placeholder="For a transgenic or mutant line, or a wild type not listed"
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
                      name={rearingName}
                      value={option}
                      checked={rearing === option}
                      onChange={() => setRearing(option)}
                    />
                    {option}
                  </RadioLabel>
                ))}
              </RadioGroup>
            )}
          </Field>

          {rearing === "Non-standard" && (
            <Field wide label="Describe the conditions" required>
              {(id) => <TextArea id={id} rows={3} />}
            </Field>
          )}
      </FieldGrid>

      <OptionalNotes />
    </EntryCard>
  );
};

export default FishSection;
