import { useState } from "react";
import {
  EntryCard,
  FieldGrid,
  MeasureGrid,
  RadioGroup,
  RadioItem,
  RadioLabel,
  MeasureRow,
  SelectInput,
  TextArea,
  TextInput,
} from "@/styles/elements";
import { useFormContext } from "react-hook-form";
import Field from "../Field";
import OptionalNotes from "../OptionalNotes";
import InfoTip from "../InfoTip";
import { VEHICLE_LABELS, VEHICLE_UNITS } from "../vehicles";
import { supplierLabel } from "../suppliers";
import QuantityField from "../QuantityField";
import StageField from "../StageField";
import { asNumber, useQuantity } from "../quantity";
import {
  CONCENTRATION_INFO,
  REARING_INFO,
  REGIMEN_INFO,
} from "../explanations";
import {
  ExposureRegimenTypeEnum,
  ExposureRouteEnum,
  ManufacturerEnum,
  VehicleEnum,
} from "@/schema";
import type { Body } from "@/schema/bodies";
import ChemicalPicker, { type Staged } from "@/features/groups/ChemicalPicker";
import AddChemicalForm from "@/features/groups/AddChemicalForm";
import {
  useAddChemical,
  useCabinet,
  useChemicalNames,
  useRefreshCabinet,
} from "@/api/hooks";
import { FlaskIcon, SearchIcon } from "@/components/icons";
import {
  StockAdd,
  StockChoices,
  StockChosen,
  StockSaved,
  StockSearch,
  StockSearchButton,
} from "@/components/StockPanel";

const CONCENTRATION_UNITS = ["µM", "mg/L", "Other"];

/**
 * The exposure's chemical: from the group's cabinet, or found in the database.
 * Choosing the database swaps the panel for the search, which is the same
 * picker the cabinet dialog uses.
 */
const Substance = ({ groupId }: { groupId: number }) => {
  const [isSearching, setIsSearching] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const { setValue, watch } = useFormContext<Body<"ExposureEvent">>();
  const { data: cabinet = [] } = useCabinet(groupId);
  const chemicalId = watch("stressor.0.chemical_id") ?? "";
  // An entry, like a stressor, stores only the identifier, so names are looked up.
  const names = useChemicalNames([
    ...cabinet.map((row) => row.chemical_id),
    ...(chemicalId ? [chemicalId] : []),
  ]);

  const addChemical = useAddChemical(groupId);
  const refreshCabinet = useRefreshCabinet(groupId);
  const isInCabinet = cabinet.some((row) => row.chemical_id === chemicalId);

  const take = (chebiId: string) => {
    setValue("stressor.0.chemical_id", chebiId, {
      shouldDirty: true,
      shouldValidate: true,
    });
    setIsSearching(false);
  };

  const clear = () =>
    setValue("stressor.0.chemical_id", null, { shouldDirty: true });

  // What was chosen, in place of the two ways of choosing it.
  if (chemicalId) {
    const name = names.get(chemicalId) ?? chemicalId;
    return (
      <StockChosen
        icon={<FlaskIcon />}
        name={name}
        // A chemical with no name stands under its own identifier.
        detail={name !== chemicalId ? chemicalId : undefined}
        actions={
          // Found in the database but not on the group's shelf: offered here
          // so the next exposure event can pick it from the cabinet.
          isInCabinet ? (
            addChemical.isSuccess && <StockSaved>Saved for reuse</StockSaved>
          ) : (
            <StockAdd
              type="button"
              onClick={() =>
                addChemical.mutate(
                  { chemicalId },
                  { onSuccess: refreshCabinet },
                )
              }
              disabled={addChemical.isPending}
            >
              {addChemical.isPending ? "Adding…" : "Add to cabinet"}
            </StockAdd>
          )
        }
        onChange={clear}
        isDisabled={addChemical.isPending}
      />
    );
  }

  if (isSearching) {
    return (
      <StockSearch
        title="Search ChEBI"
        lead="Search the database when the chemical is not in your cabinet."
        backLabel="Use cabinet"
        onBack={() => setIsSearching(false)}
      >
        <ChemicalPicker onPick={(chemical: Staged) => take(chemical.chebiId)} />
      </StockSearch>
    );
  }

  return (
    <StockChoices
      title={`From your cabinet (${cabinet.length} chemical${cabinet.length === 1 ? "" : "s"})`}
      selectLabel="Select a chemical from your cabinet"
      placeholder="Select a chemical"
      options={cabinet.map((row) => {
        const name = names.get(row.chemical_id) ?? row.chemical_id;
        return {
          value: row.chemical_id,
          label: row.nickname ? `${row.nickname} — ${name}` : name,
        };
      })}
      onPick={take}
      emptyText="Your cabinet is empty."
      whenEmpty={
        <StockAdd type="button" onClick={() => setIsAdding(true)}>
          + Add chemical
        </StockAdd>
      }
      alternatives={
        <StockSearchButton type="button" onClick={() => setIsSearching(true)}>
          <SearchIcon />
          Search ChEBI
        </StockSearchButton>
      }
    >
      <AddChemicalForm
        groupId={groupId}
        open={isAdding}
        onClose={() => setIsAdding(false)}
      />
    </StockChoices>
  );
};

type Route = `${ExposureRouteEnum}`;
type Regimen = `${ExposureRegimenTypeEnum}`;

const ROUTES: { value: Route; label: string }[] = [
  {
    value: "aquatic_environment",
    label: "via environment (chemical added to fish water)",
  },
  { value: "ingestion", label: "via diet (ingestion)" },
  { value: "gavage", label: "via gavage" },
  { value: "injection", label: "via injection" },
];

const REGIMEN_LABELS: Record<Regimen, string> = {
  continuous: "Continuous exposure",
  single: "Single exposure",
  repeated: "Repeated exposures",
};

/** Sustained exposure is "continuous"; the other routes call it a single dose. */
const regimens = (route: Route): [Regimen, Regimen] =>
  route === "aquatic_environment"
    ? ["continuous", "repeated"]
    : ["single", "repeated"];

const DURATION_UNITS = ["minute", "hour", "day"];

/** The stressor's concentration: a number, with its unit chosen beside it. */
const Concentration = () => {
  const quantity = useQuantity(
    "stressor.0.concentration",
    CONCENTRATION_UNITS[0]!,
  );

  return (
    <MeasureGrid>
      <Field
        label="Substance concentration"
        name="stressor.0.concentration.numeric_value"
        error={quantity.error}
        info={<p>{CONCENTRATION_INFO}</p>}
      >
        {(id, _labelId, errorProps) => (
          <TextInput
            id={id}
            inputMode="decimal"
            placeholder="e.g. 10"
            value={quantity.text}
            onChange={(event) => quantity.type(event.target.value)}
            onBlur={quantity.onBlur}
            {...errorProps}
          />
        )}
      </Field>

      <Field label="Unit" labels="value">
        {(_id, labelId) => (
          <RadioGroup role="radiogroup" aria-labelledby={labelId}>
            {CONCENTRATION_UNITS.map((unit) => (
              <RadioLabel key={unit}>
                <input
                  type="radio"
                  checked={quantity.unit === unit}
                  onChange={() => quantity.choose(unit)}
                />
                {unit}
              </RadioLabel>
            ))}
          </RadioGroup>
        )}
      </Field>
    </MeasureGrid>
  );
};

/**
 * One exposure event: what the fish met, by what route, and for how long.
 * The schema's exposure pattern has no slot yet, so it is not asked for.
 */
export const ExposureFields = ({ groupId }: { groupId: number }) => {
  const { register, watch, setValue } =
    useFormContext<Body<"ExposureEvent">>();
  const [route, regimen, supplier, vehicle, vehicleSupplier] = watch([
    "route",
    "regimen.exposure_regimen_type",
    "stressor.0.manufacturer",
    "vehicle.0.vehicle_type",
    "vehicle.0.manufacturer",
  ]);

  // The regimen options differ by route, so a route change picks the first of
  // the new set rather than leaving a value the radios no longer offer.
  const chooseRoute = (next: Route) => {
    setValue("route", next, { shouldDirty: true });
    setValue("regimen.exposure_regimen_type", regimens(next)[0], {
      shouldDirty: true,
    });
  };

  const repeated = regimen === "repeated";
  const sustained = regimen === "continuous";

  return (
    <>
      <Substance groupId={groupId} />

      <FieldGrid>
        <Concentration />

        <Field
          label="Chemical supplier of the test substance"
          name="stressor.0.manufacturer"
        >
          {(id, _labelId, errorProps) => (
            <SelectInput
              id={id}
              {...errorProps}
              {...register("stressor.0.manufacturer")}
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

        {/* The schema requires the name when the controlled list is escaped;
            without it the entry records no recoverable supplier. */}
        {supplier === ManufacturerEnum.other_not_listed && (
          <Field
            label="Supplier name"
            name="stressor.0.unrecognized_manufacturer_name"
          >
            {(id, _labelId, errorProps) => (
              <TextInput
                id={id}
                placeholder="Enter the supplier's name"
                {...errorProps}
                {...register("stressor.0.unrecognized_manufacturer_name", {
                  shouldUnregister: true,
                })}
              />
            )}
          </Field>
        )}

        <Field label="Vehicle of dilution" name="vehicle.0.vehicle_type">
          {(id, _labelId, errorProps) => (
            <SelectInput
              id={id}
              {...errorProps}
              {...register("vehicle.0.vehicle_type")}
            >
              <option value="">Select a vehicle</option>
              {Object.values(VehicleEnum).map((each) => (
                <option key={each} value={each}>
                  {VEHICLE_LABELS[each]}
                </option>
              ))}
            </SelectInput>
          )}
        </Field>

        {/* As with the supplier: the schema requires a name for "other". */}
        {vehicle === VehicleEnum.other_not_listed && (
          <Field
            label="Vehicle name"
            name="vehicle.0.unrecognized_chemical_name"
          >
            {(id, _labelId, errorProps) => (
              <TextInput
                id={id}
                placeholder="Enter the vehicle's name"
                {...errorProps}
                {...register("vehicle.0.unrecognized_chemical_name", {
                  shouldUnregister: true,
                })}
              />
            )}
          </Field>
        )}

        <QuantityField
          label="Vehicle concentration"
          placeholder="e.g. 0.1"
          units={VEHICLE_UNITS}
          name="vehicle.0.concentration"
        />

        <Field label="Supplier of the vehicle" name="vehicle.0.manufacturer">
          {(id, _labelId, errorProps) => (
            <SelectInput
              id={id}
              {...errorProps}
              {...register("vehicle.0.manufacturer")}
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

        {vehicleSupplier === ManufacturerEnum.other_not_listed && (
          <Field
            label="Vehicle supplier name"
            name="vehicle.0.unrecognized_manufacturer_name"
          >
            {(id, _labelId, errorProps) => (
              <TextInput
                id={id}
                placeholder="Enter the supplier's name"
                {...errorProps}
                {...register("vehicle.0.unrecognized_manufacturer_name", {
                  shouldUnregister: true,
                })}
              />
            )}
          </Field>
        )}

        <Field wide label="Exposure route" required labels="value">
          {(_id, labelId) => (
            <RadioGroup role="radiogroup" aria-labelledby={labelId}>
              {ROUTES.map((option) => (
                <RadioLabel key={option.value}>
                  <input
                    type="radio"
                    checked={route === option.value}
                    onChange={() => chooseRoute(option.value)}
                  />
                  {option.label}
                </RadioLabel>
              ))}
            </RadioGroup>
          )}
        </Field>

        {route && (
          <Field wide label="Exposure regimen" labels="value">
            {(_id, labelId) => (
              <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                {regimens(route).map((option) => (
                  <RadioItem key={option}>
                    <RadioLabel>
                      <input
                        type="radio"
                        value={option}
                        {...register("regimen.exposure_regimen_type")}
                      />
                      {REGIMEN_LABELS[option]}
                    </RadioLabel>
                    {REGIMEN_INFO[REGIMEN_LABELS[option]] && (
                      <InfoTip label={REGIMEN_LABELS[option]}>
                        <p>{REGIMEN_INFO[REGIMEN_LABELS[option]]}</p>
                      </InfoTip>
                    )}
                  </RadioItem>
                ))}
              </RadioGroup>
            )}
          </Field>
        )}

        <MeasureGrid>
          {sustained && (
            <QuantityField
              label="Exposure duration"
              placeholder="e.g. 24"
              units={DURATION_UNITS}
              name="regimen.total_exposure_duration"
            />
          )}

          {repeated && (
            <>
              <QuantityField
                label="Duration per exposure"
                placeholder="e.g. 24"
                units={DURATION_UNITS}
                name="regimen.individual_exposure_duration"
              />
              <Field
                label="Number of exposures"
                name="regimen.number_of_individual_exposure"
              >
                {(id, _labelId, errorProps) => (
                  <MeasureRow>
                    <TextInput
                      id={id}
                      inputMode="numeric"
                      placeholder="e.g. 3"
                      {...errorProps}
                      {...register("regimen.number_of_individual_exposure", {
                        setValueAs: asNumber,
                      })}
                    />
                  </MeasureRow>
                )}
              </Field>
              <QuantityField
                label="Interval between exposures"
                placeholder="e.g. 24"
                units={DURATION_UNITS}
                name="regimen.interval_between_individual_exposures"
              />
              <QuantityField
                label="Total duration of exposure"
                placeholder="e.g. 24"
                units={DURATION_UNITS}
                name="regimen.total_exposure_duration"
              />
            </>
          )}

          <StageField label="Start stage" name="exposure_start_stage" />
          <StageField label="End stage" name="exposure_end_stage" />
        </MeasureGrid>

        <Field
          wide
          label="Additional exposure condition"
          hint="Anything else about the conditions the exposure took place under."
        >
          {(id) => (
            <TextInput id={id} {...register("additional_exposure_condition")} />
          )}
        </Field>
      </FieldGrid>

      <OptionalNotes name="comment" />
    </>
  );
};

const REARING = [
  { value: true, label: "Standard" },
  { value: false, label: "Non-standard" },
];

/** Per experiment, not per exposure: the schema has it on Experiment. */
export const Rearing = () => {
  const { register, watch, setValue } = useFormContext<Body<"Experiment">>();
  const isStandard = watch("standard_rearing_condition");

  return (
    <EntryCard>
      <FieldGrid>
        {/* A group of radios has no one control to point `for` at, so the
            label is a span and the group is named by it. */}
        <Field wide label="Fish rearing conditions" labels="value">
          {(_id, labelId) => (
            <RadioGroup role="radiogroup" aria-labelledby={labelId}>
              {REARING.map((option) => (
                <RadioItem key={option.label}>
                  <RadioLabel>
                    {/* A radio's own value is text; the slot is a yes or no. */}
                    <input
                      type="radio"
                      checked={isStandard === option.value}
                      onChange={() =>
                        setValue("standard_rearing_condition", option.value, {
                          shouldDirty: true,
                        })
                      }
                    />
                    {option.label}
                  </RadioLabel>
                  {REARING_INFO[option.label] && (
                    <InfoTip label={`${option.label} rearing`}>
                      <p>{REARING_INFO[option.label]}</p>
                    </InfoTip>
                  )}
                </RadioItem>
              ))}
            </RadioGroup>
          )}
        </Field>

        {isStandard === false && (
          <Field
            wide
            label="Describe the conditions"
            name="rearing_condition_comment"
          >
            {(id, _labelId, errorProps) => (
              <TextArea
                id={id}
                rows={3}
                {...errorProps}
                {...register("rearing_condition_comment", {
                  shouldUnregister: true,
                })}
              />
            )}
          </Field>
        )}
      </FieldGrid>
    </EntryCard>
  );
};
