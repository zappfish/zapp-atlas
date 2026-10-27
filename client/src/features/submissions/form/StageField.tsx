import { useFormContext, useWatch, type FieldPath } from "react-hook-form";
import { MeasureRow, ShortSelect, TextInput } from "@/styles/elements";
import Field from "./Field";
import { STAGE_UNITS, stageAt } from "./stages";
import type { Submission } from "./submission";
import { stageTime } from "./validation";

/** A number and its unit; the ZFS stage they fall in is shown, and is what the
 *  schema stores. */
const StageField = ({
  label,
  name,
  unitName,
  required = false,
}: {
  label: string;
  name: FieldPath<Submission>;
  unitName: FieldPath<Submission>;
  required?: boolean;
}) => {
  const { register, control } = useFormContext<Submission>();
  const [value, unit] = useWatch({ control, name: [name, unitName] });
  const stage =
    typeof value === "string" && typeof unit === "string"
      ? stageAt(value, unit)
      : undefined;

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
        <MeasureRow>
          <TextInput
            id={id}
            inputMode="decimal"
            placeholder="e.g. 72"
            {...errorProps}
            {...register(name, stageTime(unitName))}
          />
          <ShortSelect
            aria-label={`${label} unit`}
            {...register(unitName, { deps: name })}
          >
            {STAGE_UNITS.map((each) => (
              <option key={each}>{each}</option>
            ))}
          </ShortSelect>
        </MeasureRow>
      )}
    </Field>
  );
};

export default StageField;
