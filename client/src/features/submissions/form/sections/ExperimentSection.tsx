import { useCallback, useState } from "react";
import {
  AddButton,
  AddRow,
  EntryCard,
  EntryHead,
  EntryRemove,
  EntryTitle,
  FieldGrid,
  MeasureGrid,
  RadioGroup,
  RadioLabel,
  MeasureRow,
  SelectInput,
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
import ChemicalPicker, { type Staged } from "@/features/groups/ChemicalPicker";
import { useCabinet, useChemical } from "@/api/hooks";
import { FlaskIcon, SearchIcon } from "@/components/icons";
import {
  SubstanceBack,
  SubstanceBody,
  SubstanceCard,
  SubstanceChange,
  SubstanceChoices,
  SubstanceChosen,
  SubstanceIcon,
  SubstanceId,
  SubstanceName,
  SubstanceNames,
  SubstanceHead,
  SubstanceLead,
  SubstanceOr,
  SubstanceSearch,
  SubstanceTitle,
} from "@/styles/elements";

const CONCENTRATION_UNITS = ["µM", "mg/L", "Other"];

/** A cabinet row. The entry stores only an identifier, so the name is looked
 *  up; until one is stored the identifier stands in for it. */
const CabinetOption = ({ chemicalId }: { chemicalId: string }) => {
  const { data } = useChemical(chemicalId);
  return <option value={chemicalId}>{data?.label ?? chemicalId}</option>;
};

/**
 * The exposure's chemical: from the group's cabinet, or found in the database.
 * Choosing the database swaps the panel for the search, which is the same
 * picker the cabinet dialog uses.
 */
const Substance = ({
  groupId,
  at,
}: {
  groupId: number;
  at: `exposures.${number}`;
}) => {
  const [isSearching, setIsSearching] = useState(false);
  const { setValue, watch } = useFormContext<Submission>();
  const { data: cabinet = [] } = useCabinet(groupId);
  const hasCabinet = cabinet.length > 0;

  const [substance, identifier] = watch([`${at}.substance`, `${at}.identifier`]);

  const take = (chebiId: string, name: string) => {
    setValue(`${at}.substance`, name || chebiId);
    setValue(`${at}.idType`, "CHEBI");
    setValue(`${at}.identifier`, chebiId);
    setIsSearching(false);
  };

  const clear = () => {
    setValue(`${at}.substance`, "");
    setValue(`${at}.idType`, "");
    setValue(`${at}.identifier`, "");
  };

  // What was chosen, in place of the two ways of choosing it.
  if (identifier) {
    return (
      <SubstanceCard>
        <SubstanceChosen>
          <SubstanceIcon aria-hidden="true">
            <FlaskIcon />
          </SubstanceIcon>
          <SubstanceNames>
            <SubstanceName>{substance}</SubstanceName>
            {/* A chemical with no name stands under its own identifier. */}
            {substance !== identifier && <SubstanceId>{identifier}</SubstanceId>}
          </SubstanceNames>
          <SubstanceChange type="button" onClick={clear}>
            Change
          </SubstanceChange>
        </SubstanceChosen>
      </SubstanceCard>
    );
  }

  if (isSearching || !hasCabinet) {
    return (
      <SubstanceCard>
        <SubstanceHead>
          <div>
            <SubstanceTitle>Search ChEBI</SubstanceTitle>
            <SubstanceLead>
              Search the database when the chemical is not in your cabinet.
            </SubstanceLead>
          </div>
          {hasCabinet && (
            <SubstanceBack type="button" onClick={() => setIsSearching(false)}>
              Use cabinet
            </SubstanceBack>
          )}
        </SubstanceHead>
        <SubstanceBody>
          <ChemicalPicker
            onPick={(chemical: Staged) =>
              take(chemical.chebiId, chemical.name)
            }
          />
        </SubstanceBody>
      </SubstanceCard>
    );
  }

  return (
    <SubstanceCard>
      <SubstanceBody>
        <SubstanceTitle>
          From your cabinet ({cabinet.length} chemical
          {cabinet.length === 1 ? "" : "s"})
        </SubstanceTitle>
        <SubstanceChoices>
          <SelectInput
            defaultValue=""
            aria-label="Select a chemical from your cabinet"
            onChange={(e) => {
              const option = e.target.selectedOptions[0];
              if (e.target.value) take(e.target.value, option?.text ?? "");
            }}
          >
            <option value="" disabled>
              Select a chemical
            </option>
            {cabinet.map((row) => (
              <CabinetOption key={row.id} chemicalId={row.chemical_id} />
            ))}
          </SelectInput>

          <SubstanceOr>OR</SubstanceOr>

          <SubstanceSearch type="button" onClick={() => setIsSearching(true)}>
            <SearchIcon />
            Search ChEBI
          </SubstanceSearch>
        </SubstanceChoices>
      </SubstanceBody>
    </SubstanceCard>
  );
};

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
    <Field label={label}>
      {(id) => (
        <MeasureRow>
          <TextInput id={id} placeholder={placeholder} {...register(name)} />
          <SelectInput
            className="field__input--short"
            aria-label={`${label} unit`}
            {...register(unitName)}
          >
            {units.map((unit) => (
              <option key={unit}>{unit}</option>
            ))}
          </SelectInput>
        </MeasureRow>
      )}
    </Field>
  );
};

/** One exposure: what the fish met, by what route, and for how long. */
const ExposureEvent = ({
  n,
  index,
  groupId,
  onRemove,
}: {
  n: number;
  index: number;
  groupId: number;
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

      <Substance groupId={groupId} at={at} />

      <FieldGrid>
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
          <MeasureGrid>
            <UnitField
              label="Exposure duration"
              units={DURATION_UNITS}
              name={`${at}.duration`}
              unitName={`${at}.durationUnit`}
            />
          </MeasureGrid>
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

        <MeasureGrid>
          {repeated && (
            <>
              <UnitField
                label="Duration per exposure"
                units={DURATION_UNITS}
                name={`${at}.durationPerExposure`}
                unitName={`${at}.durationPerExposureUnit`}
              />
              <Field label="Number of exposures">
                {(id) => (
                  <MeasureRow>
                    <TextInput id={id} {...register(`${at}.exposureCount`)} />
                  </MeasureRow>
                )}
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
        </MeasureGrid>
      </FieldGrid>

      <OptionalNotes name={`${at}.notes`} />
    </EntryCard>
  );
};

/** The substance and the exposures it was given in. */
const ExperimentSection = ({ groupId }: { groupId: number }) => {
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
          groupId={groupId}
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
