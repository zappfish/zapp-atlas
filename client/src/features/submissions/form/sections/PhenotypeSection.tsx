import { useCallback, useId, useRef, useState } from "react";
import {
  AddButton,
  AddRow,
  EntryCaret,
  EntryCard,
  EntryHead,
  EntryRemove,
  FieldNote,
  FieldPairs,
  FullRow,
  GroupSummaryText,
  GroupToggle,
  MeasureInput,
  MeasureSuffix,
  RadioGroup,
  RadioLabel,
  SelectInput,
  TextInput,
  ValueAndUnit,
} from "@/styles/elements";
import Field from "../Field";

const STAGE_UNITS = ["hpf", "dpf", "month"];
const SEVERITIES = ["Mild", "Moderate", "Severe"];

/** A phenotype seen in the exposed fish, and how strongly. */
const Observation = ({ n, onRemove }: { n: number; onRemove?: () => void }) => {
  const [isOpen, setIsOpen] = useState(n === 1);
  const toggle = useCallback(() => setIsOpen((was) => !was), []);

  const [phenotype, setPhenotype] = useState("");
  const [severity, setSeverity] = useState("");
  const severityName = useId();

  // Only what has been filled in: an empty observation says nothing.
  const summary = [severity].filter(Boolean);

  return (
    <EntryCard>
      <EntryHead>
        <GroupToggle type="button" onClick={toggle} aria-expanded={isOpen}>
          <EntryCaret aria-hidden="true" isOpen={isOpen}>
            ▶
          </EntryCaret>
          Observation {n}
        </GroupToggle>
        {phenotype && <GroupSummaryText>{phenotype}</GroupSummaryText>}
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
        <>
          <FieldPairs>
            <ValueAndUnit>
              <Field label="Fish stage at phenotype observation">
                {(id) => <TextInput id={id} placeholder="e.g. 96" />}
              </Field>
              <Field label="Unit">
                {(id) => (
                  <SelectInput id={id} defaultValue={STAGE_UNITS[0]}>
                    {STAGE_UNITS.map((unit) => (
                      <option key={unit}>{unit}</option>
                    ))}
                  </SelectInput>
                )}
              </Field>
            </ValueAndUnit>

            <Field label="Observed phenotype">
              {(id) => (
                <>
                  <TextInput
                    id={id}
                    value={phenotype}
                    onChange={(e) => setPhenotype(e.target.value)}
                    placeholder="Phenotype term"
                  />
                  <FieldNote>
                    Term not represented correctly? Request a new synonym — TBD
                  </FieldNote>
                </>
              )}
            </Field>

            <Field label="Prevalence">
              {(id) => (
                <MeasureInput>
                  <TextInput id={id} placeholder="e.g. 80" />
                  <MeasureSuffix>%</MeasureSuffix>
                </MeasureInput>
              )}
            </Field>

            <FullRow>
              <Field label="Severity" labels="value">
                {(_id, labelId) => (
                  <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                    {SEVERITIES.map((option) => (
                      <RadioLabel key={option}>
                        <input
                          type="radio"
                          name={severityName}
                          checked={severity === option}
                          onChange={() => setSeverity(option)}
                        />
                        {option}
                      </RadioLabel>
                    ))}
                  </RadioGroup>
                )}
              </Field>
            </FullRow>
          </FieldPairs>

        </>
      )}
    </EntryCard>
  );
};

/** The phenotypes this submission reports. */
const PhenotypeSection = () => {
  // Ids rather than a count: removing one must not renumber those after it.
  const [ids, setIds] = useState([0]);
  const next = useRef(1);
  const add = useCallback(() => setIds((was) => [...was, next.current++]), []);
  const remove = useCallback(
    (id: number) => setIds((was) => was.filter((each) => each !== id)),
    [],
  );

  return (
    <>
      {ids.map((id, i) => (
        <Observation
          key={id}
          n={i + 1}
          onRemove={ids.length > 1 ? () => remove(id) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={add}>
          + Add another observation
        </AddButton>
      </AddRow>
    </>
  );
};

export default PhenotypeSection;
