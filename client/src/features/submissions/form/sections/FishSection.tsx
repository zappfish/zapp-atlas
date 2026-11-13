import { EntryCard, FieldGrid, TextArea, TextInput } from "@/styles/elements";
import { useFormContext } from "react-hook-form";
import Field from "../Field";
import type { Submission } from "../submission";
import OptionalNotes from "../OptionalNotes";

/** The fish the experiment used. */
const FishSection = () => {
  const { register } = useFormContext<Submission>();

  return (
    <EntryCard>
      <FieldGrid>
        <Field
          label="Select existing fish"
          hint="i.e. the transgene and/or mutant line name, if applicable"
        >
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
      </FieldGrid>

      <OptionalNotes name="fish.notes" />
    </EntryCard>
  );
};

export default FishSection;
