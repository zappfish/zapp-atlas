import { useCallback, useState } from "react";
import {
  AddButton,
  AddRow,
  EntryCard,
  EntryHead,
  EntryRemove,
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
import { ManufacturerEnum, VehicleEnum } from "@/schema";
import type { Body } from "@/schema/bodies";
import Field from "../Field";
import QuantityField from "../QuantityField";
import { supplierLabel } from "../suppliers";
import { VEHICLE_LABELS, VEHICLE_UNITS } from "../vehicles";

const TYPES = ["Negative control / untreated", "Vehicle control"];

/**
 * What this control was. The schema has a type, a vehicle and a comment for
 * a control; its strain, rearing and images wait on how controls are modelled.
 */
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

  const { register, watch } = useFormContext<Body<"Experiment">>();
  const at = `control.${index}` as const;
  const [type, vehicle, supplier] = watch([
    `${at}.control_type`,
    `${at}.vehicle_if_treated.vehicle_type`,
    `${at}.vehicle_if_treated.manufacturer`,
  ]);

  // Only what has been filled in: a control with nothing entered says nothing.
  const summary = [
    type === "Vehicle control" && vehicle ? VEHICLE_LABELS[vehicle] : "",
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
        <FieldGrid>
          <Field wide label="Control type" labels="value">
            {(_id, labelId) => (
              <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                {TYPES.map((option) => (
                  <RadioLabel key={option}>
                    <input
                      type="radio"
                      value={option}
                      {...register(`${at}.control_type`)}
                    />
                    {option}
                  </RadioLabel>
                ))}
              </RadioGroup>
            )}
          </Field>

          <Field
            label="Vehicle used"
            name={`${at}.vehicle_if_treated.vehicle_type`}
          >
            {(id, _labelId, errorProps) => (
              <SelectInput
                id={id}
                {...errorProps}
                {...register(`${at}.vehicle_if_treated.vehicle_type`)}
              >
                <option value="">Select vehicle used</option>
                {Object.values(VehicleEnum).map((each) => (
                  <option key={each} value={each}>
                    {VEHICLE_LABELS[each]}
                  </option>
                ))}
              </SelectInput>
            )}
          </Field>

          {/* The schema requires a name when the list is escaped. */}
          {vehicle === VehicleEnum.other_not_listed && (
            <Field
              label="Vehicle name"
              name={`${at}.vehicle_if_treated.unrecognized_chemical_name`}
            >
              {(id, _labelId, errorProps) => (
                <TextInput
                  id={id}
                  placeholder="Enter the vehicle's name"
                  {...errorProps}
                  {...register(
                    `${at}.vehicle_if_treated.unrecognized_chemical_name`,
                    { shouldUnregister: true },
                  )}
                />
              )}
            </Field>
          )}

          <QuantityField
            label="Vehicle concentration"
            placeholder="e.g. 0.1"
            units={VEHICLE_UNITS}
            name={`${at}.vehicle_if_treated.concentration`}
          />

          <Field
            label="Supplier of the vehicle"
            name={`${at}.vehicle_if_treated.manufacturer`}
          >
            {(id, _labelId, errorProps) => (
              <SelectInput
                id={id}
                {...errorProps}
                {...register(`${at}.vehicle_if_treated.manufacturer`)}
              >
                <option value="">Select a supplier</option>
                {Object.values(ManufacturerEnum).map((each) => (
                  <option key={each} value={each}>
                    {supplierLabel(each)}
                  </option>
                ))}
              </SelectInput>
            )}
          </Field>

          {supplier === ManufacturerEnum.other_not_listed && (
            <Field
              label="Vehicle supplier name"
              name={`${at}.vehicle_if_treated.unrecognized_manufacturer_name`}
            >
              {(id, _labelId, errorProps) => (
                <TextInput
                  id={id}
                  placeholder="Enter the supplier's name"
                  {...errorProps}
                  {...register(
                    `${at}.vehicle_if_treated.unrecognized_manufacturer_name`,
                    { shouldUnregister: true },
                  )}
                />
              )}
            </Field>
          )}

          <Field wide label="Notes">
            {(id) => <TextArea id={id} rows={3} {...register(`${at}.comment`)} />}
          </Field>
        </FieldGrid>
      )}
    </EntryCard>
  );
};

/** The controls this experiment was measured against. */
const ControlSection = () => {
  const { control } = useFormContext<Body<"Experiment">>();
  const { fields, append, remove } = useFieldArray({ control, name: "control" });

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
        {/* A row with nothing filled in is not saved. */}
        <AddButton type="button" onClick={() => append({})}>
          + Add another control
        </AddButton>
      </AddRow>
    </>
  );
};

export default ControlSection;
