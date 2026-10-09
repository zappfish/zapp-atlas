import { useCallback } from "react";
import {
  AddButton,
  AddRow,
  EntryCard,
  EntryHead,
  EntryRemove,
  EntryTitle,
  FieldGrid,
  RadioGroup,
  RadioLabel,
  SelectInput,
  TextArea,
  TextInput,
} from "@/styles/elements";
import {
  useFieldArray,
  useFormContext,
  type FieldPath,
} from "react-hook-form";
import Field from "../Field";
import { emptyExposure, type Submission } from "../submission";
import OptionalNotes from "../OptionalNotes";

const ID_TYPES = ["CAS", "PubChem", "CHEBI", "None"];
const CONCENTRATION_UNITS = ["µM", "mg/L", "Other"];

const ROUTES = [
  { value: "environment", label: "via environment (ambient aquatic environment route)" },
  { value: "diet", label: "via diet (ingestion)" },
  { value: "gavage", label: "via gavage" },
  { value: "injection", label: "via injection" },
] as const;
type Route = (typeof ROUTES)[number]["value"];

/** Sustained exposure is "continuous"; the other routes call it a single dose. */
const regimens = (route: Route): [string, string] =>
  route === "environment"
    ? ["Continuous exposure", "Repeated exposures"]
    : ["Single exposure", "Repeated exposures"];

const DURATION_UNITS = ["minute", "hour", "day"];
const STAGE_UNITS = ["hpf", "dpf", "month"];

const PATTERNS = [
  "Sustained - static",
  "Sustained - static renewal",
  "Sustained - dynamic (flow through)",
];

/** A value and the unit it is measured in. */
const UnitField = ({
  label,
  units,
  placeholder,
  name,
  unitName,
}: {
  label: string;
  units: string[];
  placeholder?: string;
  name: FieldPath<Submission>;
  unitName: FieldPath<Submission>;
}) => {
  const { register } = useFormContext<Submission>();

  return (
  <>
    <Field label={label}>
      {(id) => (
        <TextInput id={id} placeholder={placeholder} {...register(name)} />
      )}
    </Field>
    <Field label="Unit">
      {(id) => (
        <SelectInput
          id={id}
          className="field__input--short"
          {...register(unitName)}
        >
          {units.map((unit) => (
            <option key={unit}>{unit}</option>
          ))}
        </SelectInput>
      )}
    </Field>
  </>
  );
};

/** One exposure: what the fish met, by what route, and for how long. */
const ExposureEvent = ({
  n,
  index,
  onRemove,
}: {
  n: number;
  index: number;
  onRemove?: () => void;
}) => {
  const { register, watch, setValue } = useFormContext<Submission>();
  const at = `exposures.${index}` as const;
  const [route, regimen] = watch([`${at}.route`, `${at}.regimen`]) as [
    Route,
    string,
  ];

  // The regimen options differ by route, so a route change picks the first of
  // the new set rather than leaving a value the radios no longer offer.
  const chooseRoute = useCallback(
    (next: Route) => {
      setValue(`${at}.route`, next);
      setValue(`${at}.regimen`, regimens(next)[0]);
    },
    [at, setValue],
  );

  const repeated = regimen === "Repeated exposures";
  const sustained = route === "environment" && !repeated;

  return (
    <EntryCard>
      <EntryHead>
        <EntryTitle>Exposure event {n}</EntryTitle>
        {onRemove && (
          <EntryRemove type="button" onClick={onRemove}>
            Remove
          </EntryRemove>
        )}
      </EntryHead>

      <FieldGrid>
        <Field label="Substance" required>
          {(id) => <TextInput
              id={id}
              placeholder="Substance label"
              {...register(`${at}.substance`)}
            />}
        </Field>

        <Field label="Substance / chemical description">
          {(id) => <TextArea id={id} rows={1} {...register(`${at}.description`)} />}
        </Field>

        <Field label="ID type">
          {(id) => (
            <SelectInput id={id} {...register(`${at}.idType`)}>
              {ID_TYPES.map((type) => (
                <option key={type}>{type}</option>
              ))}
            </SelectInput>
          )}
        </Field>

        <Field label="Identifier">
          {(id) => <TextInput
              id={id}
              placeholder="e.g. 50-00-0"
              {...register(`${at}.identifier`)}
            />}
        </Field>

        <Field label="Substance concentration">
          {(id) => <TextInput
              id={id}
              placeholder="e.g. 10"
              {...register(`${at}.concentration`)}
            />}
        </Field>

        <Field label="Unit" labels="value">
          {(_id, labelId) => (
            <RadioGroup role="radiogroup" aria-labelledby={labelId}>
              {CONCENTRATION_UNITS.map((unit) => (
                <RadioLabel key={unit}>
                  <input
                    type="radio"
                    value={unit}
                    {...register(`${at}.concentrationUnit`)}
                  />
                  {unit}
                </RadioLabel>
              ))}
            </RadioGroup>
          )}
        </Field>

        <Field label="Chemical supplier of the test substance">
          {(id) => <TextInput
              id={id}
              placeholder="Enter supplier's name or link to website"
              {...register(`${at}.supplier`)}
            />}
        </Field>

        <Field label="Additional information on the test substance">
          {(id) => <TextInput
              id={id}
              placeholder="e.g. 99% purity"
              {...register(`${at}.additionalInformation`)}
            />}
        </Field>

        <Field label="Exposure description">
          {(id) => (
            <TextInput
              id={id}
              placeholder="e.g. 4uM of ethanol were added to water every four hours"
              {...register(`${at}.exposureDescription`)}
            />
          )}
        </Field>

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

          <Field wide label="Exposure regimen" labels="value">
            {(_id, labelId) => (
              <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                {regimens(route).map((option) => (
                  <RadioLabel key={option}>
                    <input
                      type="radio"
                      value={option}
                      {...register(`${at}.regimen`)}
                    />
                    {option}
                  </RadioLabel>
                ))}
              </RadioGroup>
            )}
          </Field>

        {sustained && (
          <UnitField
            label="Exposure duration"
            units={DURATION_UNITS}
            name={`${at}.duration`}
            unitName={`${at}.durationUnit`}
          />
        )}

        {sustained && (
            <Field wide label="Exposure pattern" labels="value">
              {(_id, labelId) => (
                <RadioGroup role="group" aria-labelledby={labelId}>
                  {PATTERNS.map((pattern) => (
                    <RadioLabel key={pattern}>
                      <input
                      type="checkbox"
                      value={pattern}
                      {...register(`${at}.pattern`)}
                    />
                      {pattern}
                    </RadioLabel>
                  ))}
                </RadioGroup>
              )}
            </Field>
        )}

        {repeated && (
          <>
            <UnitField
              label="Duration per exposure"
              units={DURATION_UNITS}
              name={`${at}.durationPerExposure`}
              unitName={`${at}.durationPerExposureUnit`}
            />
            <Field label="Number of exposures">
              {(id) => <TextInput id={id} {...register(`${at}.exposureCount`)} />}
            </Field>
            <UnitField
              label="Interval between exposures"
              units={DURATION_UNITS}
              name={`${at}.interval`}
              unitName={`${at}.intervalUnit`}
            />
            <UnitField
              label="Total duration of exposure"
              units={DURATION_UNITS}
              name={`${at}.totalDuration`}
              unitName={`${at}.totalDurationUnit`}
            />
          </>
        )}

        <UnitField
          label="Start stage value"
          units={STAGE_UNITS}
          name={`${at}.startStage`}
          unitName={`${at}.startStageUnit`}
        />
        <UnitField
          label="End stage value"
          units={STAGE_UNITS}
          name={`${at}.endStage`}
          unitName={`${at}.endStageUnit`}
        />
      </FieldGrid>

      <OptionalNotes name={`${at}.notes`} />
    </EntryCard>
  );
};

/** The substance and the exposures it was given in. */
const ExperimentSection = () => {
  const { control } = useFormContext<Submission>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: "exposures",
  });

  return (
    <>
      {fields.map((field, i) => (
        <ExposureEvent
          key={field.id}
          n={i + 1}
          index={i}
          onRemove={fields.length > 1 ? () => remove(i) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={() => append(emptyExposure())}>
          + Add another exposure
        </AddButton>
      </AddRow>
    </>
  );
};

export default ExperimentSection;
