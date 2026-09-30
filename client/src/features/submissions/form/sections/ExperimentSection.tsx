import { useCallback, useId, useRef, useState } from "react";
import {
  AddButton,
  AddRow,
  EntryCard,
  EntryFooter,
  EntryHead,
  EntryRemove,
  EntryTitle,
  FieldGrid,
  Notes,
  NotesRemove,
  NotesToggle,
  RadioGroup,
  RadioLabel,
  SelectInput,
  TextArea,
  TextInput,
} from "@/styles/elements";
import Field from "../Field";

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
}: {
  label: string;
  units: string[];
  placeholder?: string;
}) => (
  <>
    <Field label={label}>
      {(id) => <TextInput id={id} placeholder={placeholder} />}
    </Field>
    <Field label="Unit">
      {(id) => (
        <SelectInput id={id} defaultValue={units[0]} className="field__input--short">
          {units.map((unit) => (
            <option key={unit}>{unit}</option>
          ))}
        </SelectInput>
      )}
    </Field>
  </>
);

/** One exposure: what the fish met, by what route, and for how long. */
const ExposureEvent = ({
  n,
  onRemove,
}: {
  n: number;
  onRemove?: () => void;
}) => {
  const [notesOpen, setNotesOpen] = useState(false);
  const openNotes = useCallback(() => setNotesOpen(true), []);
  const closeNotes = useCallback(() => setNotesOpen(false), []);

  const [route, setRoute] = useState<Route>("environment");
  const [regimen, setRegimen] = useState("Continuous exposure");
  const routeName = useId();
  const regimenName = useId();

  // The regimen options differ by route, so a route change picks the first of
  // the new set rather than leaving a value the radios no longer offer.
  const chooseRoute = useCallback((next: Route) => {
    setRoute(next);
    setRegimen(regimens(next)[0]);
  }, []);

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
          {(id) => <TextInput id={id} placeholder="Substance label" />}
        </Field>

        <Field label="Substance / chemical description">
          {(id) => <TextArea id={id} rows={1} />}
        </Field>

        <Field label="ID type">
          {(id) => (
            <SelectInput id={id} defaultValue={ID_TYPES[0]}>
              {ID_TYPES.map((type) => (
                <option key={type}>{type}</option>
              ))}
            </SelectInput>
          )}
        </Field>

        <Field label="Identifier">
          {(id) => <TextInput id={id} placeholder="e.g. 50-00-0" />}
        </Field>

        <Field label="Substance concentration">
          {(id) => <TextInput id={id} placeholder="e.g. 10" />}
        </Field>

        <Field label="Unit" labels="value">
          {(_id, labelId) => (
            <RadioGroup role="radiogroup" aria-labelledby={labelId}>
              {CONCENTRATION_UNITS.map((unit) => (
                <RadioLabel key={unit}>
                  <input type="radio" name={`${routeName}-conc`} defaultChecked={unit === "µM"} />
                  {unit}
                </RadioLabel>
              ))}
            </RadioGroup>
          )}
        </Field>

        <Field label="Chemical supplier of the test substance">
          {(id) => <TextInput id={id} placeholder="Enter supplier's name or link to website" />}
        </Field>

        <Field label="Additional information on the test substance">
          {(id) => <TextInput id={id} placeholder="e.g. 99% purity" />}
        </Field>

        <Field label="Exposure description">
          {(id) => (
            <TextInput
              id={id}
              placeholder="e.g. 4uM of ethanol were added to water every four hours"
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
                      name={routeName}
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
                      name={regimenName}
                      checked={regimen === option}
                      onChange={() => setRegimen(option)}
                    />
                    {option}
                  </RadioLabel>
                ))}
              </RadioGroup>
            )}
          </Field>

        {sustained && (
          <UnitField label="Exposure duration" units={DURATION_UNITS} />
        )}

        {sustained && (
            <Field wide label="Exposure pattern" labels="value">
              {(_id, labelId) => (
                <RadioGroup role="group" aria-labelledby={labelId}>
                  {PATTERNS.map((pattern) => (
                    <RadioLabel key={pattern}>
                      <input type="checkbox" name={`${routeName}-pattern`} />
                      {pattern}
                    </RadioLabel>
                  ))}
                </RadioGroup>
              )}
            </Field>
        )}

        {repeated && (
          <>
            <UnitField label="Duration per exposure" units={DURATION_UNITS} />
            <Field label="Number of exposures">
              {(id) => <TextInput id={id} />}
            </Field>
            <UnitField label="Interval between exposures" units={DURATION_UNITS} />
            <UnitField label="Total duration of exposure" units={DURATION_UNITS} />
          </>
        )}

        <UnitField label="Start stage value" units={STAGE_UNITS} />
        <UnitField label="End stage value" units={STAGE_UNITS} />
      </FieldGrid>

      <EntryFooter>
        {notesOpen ? (
          <Notes>
            <Field label="Notes">{(id) => <TextArea id={id} rows={3} />}</Field>
            <NotesRemove type="button" onClick={closeNotes}>
              Remove notes
            </NotesRemove>
          </Notes>
        ) : (
          <NotesToggle type="button" onClick={openNotes}>
            Add notes
          </NotesToggle>
        )}
      </EntryFooter>
    </EntryCard>
  );
};

/** The substance and the exposures it was given in. */
const ExperimentSection = () => {
  // Ids rather than a count: removing one must not renumber the state of the
  // events after it.
  const [ids, setIds] = useState([0]);
  const next = useRef(1);

  const add = useCallback(() => {
    setIds((was) => [...was, next.current++]);
  }, []);

  const remove = useCallback((id: number) => {
    setIds((was) => was.filter((each) => each !== id));
  }, []);

  return (
    <>
      {ids.map((id, i) => (
        <ExposureEvent
          key={id}
          n={i + 1}
          onRemove={ids.length > 1 ? () => remove(id) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={add}>
          + Add another exposure
        </AddButton>
      </AddRow>
    </>
  );
};

export default ExperimentSection;
