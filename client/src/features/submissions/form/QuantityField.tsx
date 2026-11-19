import { MeasureRow, ShortSelect, TextInput } from "@/styles/elements";
import Field from "./Field";
import { useQuantity } from "./quantity";

/** A value and the unit it is measured in, stored as one quantity. */
const QuantityField = ({
  label,
  units,
  placeholder,
  name,
}: {
  label: string;
  units: string[];
  placeholder?: string;
  /** The quantity's slot. */
  name: string;
}) => {
  const quantity = useQuantity(name, units[0]!);

  return (
    <Field label={label} name={`${name}.numeric_value`} error={quantity.error}>
      {(id, _labelId, errorProps) => (
        <MeasureRow>
          <TextInput
            id={id}
            inputMode="decimal"
            placeholder={placeholder}
            value={quantity.text}
            onChange={(event) => quantity.type(event.target.value)}
            onBlur={quantity.onBlur}
            {...errorProps}
          />
          <ShortSelect
            aria-label={`${label} unit`}
            value={quantity.unit}
            onChange={(event) => quantity.choose(event.target.value)}
          >
            {units.map((unit) => (
              <option key={unit}>{unit}</option>
            ))}
          </ShortSelect>
        </MeasureRow>
      )}
    </Field>
  );
};

export default QuantityField;
