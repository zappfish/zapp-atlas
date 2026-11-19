import { useState } from "react";
import { useController } from "react-hook-form";
import { MeasureRow, ShortSelect, TextInput } from "@/styles/elements";
import Field from "./Field";
import { STAGE_UNITS, ZFS_STAGES, stageAt, type Stage } from "./stages";

const describe = (stage: Stage) =>
  `ZFS stage: ${stage.period}${stage.name === stage.period ? "" : `: ${stage.name}`} (${stage.id})`;

/**
 * A time, as a number and its unit, for a slot that holds a ZFS stage.
 *
 * The form's value is the stage the time falls in, which is what the schema
 * stores. What was typed is held here and not kept: a saved stage comes back
 * as its name and the hours it covers.
 */
const StageField = ({
  label,
  name,
  required = false,
}: {
  label: string;
  /** The slot the stage is stored in. */
  name: string;
  required?: boolean;
}) => {
  const { field } = useController({ name });
  const [text, setText] = useState("");
  const [unit, setUnit] = useState(STAGE_UNITS[0]!);

  const hold = (nextText: string, nextUnit: string) => {
    setText(nextText);
    setUnit(nextUnit);
    field.onChange(stageAt(nextText, nextUnit)?.id);
  };

  const typed = text.trim() !== "";
  const saved = ZFS_STAGES.find((stage) => stage.id === field.value);
  const error = !typed
    ? undefined
    : !/^\d+(\.\d+)?$/.test(text.trim())
      ? "Enter a number, e.g. 72."
      : saved === undefined
        ? "No ZFS stage covers that time."
        : undefined;

  return (
    <Field
      label={label}
      name={name}
      error={error}
      required={required}
      hint={
        saved &&
        (typed
          ? describe(saved)
          : `${describe(saved)}, ${saved.start} to ${saved.end} hpf`)
      }
    >
      {(id, _labelId, errorProps) => (
        <MeasureRow>
          <TextInput
            id={id}
            inputMode="decimal"
            placeholder="e.g. 72"
            value={text}
            onChange={(event) => hold(event.target.value, unit)}
            onBlur={field.onBlur}
            {...errorProps}
          />
          <ShortSelect
            aria-label={`${label} unit`}
            value={unit}
            onChange={(event) => hold(text, event.target.value)}
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
