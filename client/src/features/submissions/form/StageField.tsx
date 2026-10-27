import { useFormContext, useWatch, type FieldPath } from "react-hook-form";
import { TextInput } from "@/styles/elements";
import Field from "./Field";
import { stageAt } from "./stages";
import type { Submission } from "./submission";
import { STAGE_TIME } from "./validation";

/** Typed as a time; the ZFS stage it falls in is shown, and is what the
 *  schema stores. */
const StageField = ({
  label,
  name,
  required = false,
}: {
  label: string;
  name: FieldPath<Submission>;
  required?: boolean;
}) => {
  const { register, control } = useFormContext<Submission>();
  const value = useWatch({ control, name });
  const stage = typeof value === "string" ? stageAt(value) : undefined;

  return (
    <Field
      label={label}
      name={name}
      required={required}
      hint={
        stage
          ? `ZFS stage: ${stage.period}${stage.name === stage.period ? "" : `: ${stage.name}`} (${stage.id})`
          : undefined
      }
    >
      {(id, _labelId, errorProps) => (
        <TextInput
          id={id}
          placeholder="e.g. 72 hpf or 5 dpf"
          {...errorProps}
          {...register(name, STAGE_TIME)}
        />
      )}
    </Field>
  );
};

export default StageField;
