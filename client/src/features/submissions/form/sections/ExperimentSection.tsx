import { useState } from "react";
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
  RadioItem,
  RadioLabel,
  MeasureRow,
  SelectInput,
  ShortSelect,
  SubstanceAdd,
  SubstanceBack,
  SubstanceBody,
  SubstanceCard,
  SubstanceChange,
  SubstanceChoices,
  SubstanceChosen,
  SubstanceHead,
  SubstanceIcon,
  SubstanceId,
  SubstanceLead,
  SubstanceName,
  SubstanceNames,
  SubstanceOr,
  SubstanceSaved,
  SubstanceSearch,
  SubstanceTitle,
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
import InfoTip from "../InfoTip";
import StageField from "../StageField";
import { NUMBER, WHOLE_NUMBER } from "../validation";
import {
  CONCENTRATION_INFO,
  PATTERN_INFO,
  REARING_INFO,
  REGIMEN_INFO,
} from "../explanations";
import { ManufacturerEnum } from "@/schema";
import ChemicalPicker, { type Staged } from "@/features/groups/ChemicalPicker";
import {
  useAddChemical,
  useCabinet,
  useChemicalNames,
  useRefreshCabinet,
} from "@/api/hooks";
import { FlaskIcon, SearchIcon } from "@/components/icons";

const CONCENTRATION_UNITS = ["µM", "mg/L", "Other"];

/** Spelled out rather than capitalised: "vwr" -> "VWR". */
const SUPPLIER_ACRONYMS = new Set(["vwr"]);

const supplierLabel = (value: string) =>
  value
    .split("_")
    .map((word) =>
      SUPPLIER_ACRONYMS.has(word)
        ? word.toUpperCase()
        : word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");

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
  // An entry stores only the identifier, so names are looked up.
  const names = useChemicalNames(cabinet.map((row) => row.chemical_id));

  const [substance, identifier] = watch([`${at}.substance`, `${at}.identifier`]);

  const addChemical = useAddChemical(groupId);
  const refreshCabinet = useRefreshCabinet(groupId);
  const isInCabinet = cabinet.some((row) => row.chemical_id === identifier);

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
          {/* Found in the database but not on the group's shelf: offered here
              so the next submission can pick it from the cabinet. */}
          {isInCabinet ? (
            addChemical.isSuccess && <SubstanceSaved>Saved for reuse</SubstanceSaved>
          ) : (
            <SubstanceAdd
              type="button"
              onClick={() =>
                addChemical.mutate(
                  { chemicalId: identifier },
                  { onSuccess: refreshCabinet },
                )
              }
              disabled={addChemical.isPending}
            >
              {addChemical.isPending ? "Adding…" : "Add to cabinet"}
            </SubstanceAdd>
          )}
          <SubstanceChange
            type="button"
            onClick={clear}
            disabled={addChemical.isPending}
          >
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
              const chemicalId = e.target.value;
              if (chemicalId) take(chemicalId, names.get(chemicalId) ?? "");
            }}
          >
            <option value="" disabled>
              Select a chemical
            </option>
            {cabinet.map((row) => {
              const name = names.get(row.chemical_id) ?? row.chemical_id;
              return (
                <option key={row.id} value={row.chemical_id}>
                  {row.nickname ? `${row.nickname} — ${name}` : name}
                </option>
              );
            })}
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
  rules,
}: {
  label: string;
  units: string[];
  placeholder?: string;
  name: FieldPath<Submission>;
  unitName: FieldPath<Submission>;
  rules?: typeof NUMBER;
}) => {
  const { register } = useFormContext<Submission>();

  return (
    <Field label={label} name={name}>
      {(id, _labelId, errorProps) => (
        <MeasureRow>
          <TextInput
            id={id}
            inputMode={rules ? "decimal" : undefined}
            placeholder={placeholder}
            {...errorProps}
            {...register(name, rules)}
          />
          <ShortSelect aria-label={`${label} unit`} {...register(unitName)}>
            {units.map((unit) => (
              <option key={unit}>{unit}</option>
            ))}
          </ShortSelect>
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
  const [route, regimen, supplier] = watch([
    `${at}.route`,
    `${at}.regimen`,
    `${at}.supplier`,
  ]) as [Route, string, string];

  // The regimen options differ by route, so a route change picks the first of
  // the new set rather than leaving a value the radios no longer offer.
  const chooseRoute = (next: Route) => {
    setValue(`${at}.route`, next);
    setValue(`${at}.regimen`, regimens(next)[0]);
  };

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
        <Field
          label="Substance concentration"
          name={`${at}.concentration`}
          info={<p>{CONCENTRATION_INFO}</p>}
        >
          {(id, _labelId, errorProps) => (
            <TextInput
              id={id}
              inputMode="decimal"
              placeholder="e.g. 10"
              {...errorProps}
              {...register(`${at}.concentration`, NUMBER)}
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
          {(id) => (
            <SelectInput id={id} {...register(`${at}.supplier`)}>
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
          <Field label="Supplier name">
            {(id) => (
              <TextInput
                id={id}
                placeholder="Enter the supplier's name"
                {...register(`${at}.supplierOther`)}
              />
            )}
          </Field>
        )}

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
                  <RadioItem key={option}>
                    <RadioLabel>
                      <input
                        type="radio"
                        value={option}
                        {...register(`${at}.regimen`)}
                      />
                      {option}
                    </RadioLabel>
                    {REGIMEN_INFO[option] && (
                      <InfoTip label={option}>
                        <p>{REGIMEN_INFO[option]}</p>
                      </InfoTip>
                    )}
                  </RadioItem>
                ))}
              </RadioGroup>
            )}
          </Field>

        {sustained && (
          <MeasureGrid>
            <UnitField
              label="Exposure duration"
              placeholder="e.g. 24"
              rules={NUMBER}
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
                    <RadioItem key={pattern}>
                      <RadioLabel>
                        <input
                          type="checkbox"
                          value={pattern}
                          {...register(`${at}.pattern`)}
                        />
                        {pattern}
                      </RadioLabel>
                      <InfoTip label={pattern}>
                        <p>{PATTERN_INFO[pattern]}</p>
                      </InfoTip>
                    </RadioItem>
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
                placeholder="e.g. 24"
                rules={NUMBER}
                units={DURATION_UNITS}
                name={`${at}.durationPerExposure`}
                unitName={`${at}.durationPerExposureUnit`}
              />
              <Field label="Number of exposures" name={`${at}.exposureCount`}>
                {(id, _labelId, errorProps) => (
                  <MeasureRow>
                    <TextInput
                      id={id}
                      inputMode="numeric"
                      placeholder="e.g. 3"
                      {...errorProps}
                      {...register(`${at}.exposureCount`, WHOLE_NUMBER)}
                    />
                  </MeasureRow>
                )}
              </Field>
              <UnitField
                label="Interval between exposures"
                placeholder="e.g. 24"
                rules={NUMBER}
                units={DURATION_UNITS}
                name={`${at}.interval`}
                unitName={`${at}.intervalUnit`}
              />
              <UnitField
                label="Total duration of exposure"
                placeholder="e.g. 24"
                rules={NUMBER}
                units={DURATION_UNITS}
                name={`${at}.totalDuration`}
                unitName={`${at}.totalDurationUnit`}
              />
            </>
          )}

          <StageField label="Start stage" name={`${at}.startStage`} />
          <StageField label="End stage" name={`${at}.endStage`} />
        </MeasureGrid>
      </FieldGrid>

      <OptionalNotes name={`${at}.notes`} />
    </EntryCard>
  );
};

const REARING = ["Standard", "Non-standard"];

/** Per experiment, not per exposure: the schema has it on Experiment. */
const Rearing = () => {
  const { register, watch } = useFormContext<Submission>();
  const rearing = watch("experiment.rearing");

  return (
    <EntryCard>
      <FieldGrid>
        {/* A group of radios has no one control to point `for` at, so the
            label is a span and the group is named by it. */}
        <Field wide label="Fish rearing conditions" labels="value">
          {(_id, labelId) => (
            <RadioGroup role="radiogroup" aria-labelledby={labelId}>
              {REARING.map((option) => (
                <RadioItem key={option}>
                  <RadioLabel>
                    <input
                      type="radio"
                      value={option}
                      {...register("experiment.rearing")}
                    />
                    {option}
                  </RadioLabel>
                  {REARING_INFO[option] && (
                    <InfoTip label={`${option} rearing`}>
                      <p>{REARING_INFO[option]}</p>
                    </InfoTip>
                  )}
                </RadioItem>
              ))}
            </RadioGroup>
          )}
        </Field>

        {rearing === "Non-standard" && (
          <Field wide label="Describe the conditions" required>
            {(id) => (
              <TextArea
                id={id}
                rows={3}
                {...register("experiment.rearingComment")}
              />
            )}
          </Field>
        )}
      </FieldGrid>
    </EntryCard>
  );
};

/** How the fish were reared, and the exposures they were given. */
const ExperimentSection = ({ groupId }: { groupId: number }) => {
  const { control } = useFormContext<Submission>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: "exposures",
  });

  return (
    <>
      <Rearing />

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
