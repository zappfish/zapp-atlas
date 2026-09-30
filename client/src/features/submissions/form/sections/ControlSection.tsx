import { useCallback, useId, useRef, useState } from "react";
import {
  AddButton,
  AddRow,
  AddRowInline,
  EntryBody,
  EntryCard,
  EntryHead,
  EntryMeta,
  EntryRemove,
  EntryTitle,
  FieldPairs,
  FullRow,
  EntryCaret,
  GroupSummaryText,
  GroupToggle,
  RadioGroup,
  RadioLabel,
  SelectInput,
  TextArea,
  TextInput,
} from "@/styles/elements";
import Field from "../Field";
import { ImageUpload, Measure } from "../imageEntry";
import { MEASURES } from "../measures";

const TYPES = ["Negative control / untreated", "Vehicle control"];

const VEHICLES = [
  "Dimethylformamide (DMF)",
  "Dimethyl sulfoxide (DMSO)",
  "Embryonic media (EM/E3)",
  "Ethanol",
  "Methylcellulose",
];

const REARING = ["Standard", "Not standard"];

/** One image attached to a control, with its own metadata. */
const ControlImage = ({ n, onRemove }: { n: number; onRemove: () => void }) => (
  <EntryCard>
    <EntryHead>
      <EntryTitle>Image {n}</EntryTitle>
      <EntryRemove type="button" onClick={onRemove}>
        Remove
      </EntryRemove>
    </EntryHead>

    <EntryBody>
      <ImageUpload required={false} />
      <EntryMeta>
        {MEASURES.map((measure) => (
          <Measure key={measure.label} {...measure} />
        ))}
        <Field label="Microscope information">
          {(id) => <TextInput id={id} placeholder="Enter text" />}
        </Field>
      </EntryMeta>
    </EntryBody>
  </EntryCard>
);

/** What this control was, and what it looked like. */
const Control = ({
  n,
  onRemove,
}: {
  n: number;
  onRemove?: () => void;
}) => {
  const [isOpen, setIsOpen] = useState(n === 1);
  const toggle = useCallback(() => setIsOpen((was) => !was), []);

  const [type, setType] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [strain, setStrain] = useState("");
  const [rearing, setRearing] = useState("Standard");
  const typeName = useId();
  const rearingName = useId();

  const [images, setImages] = useState<number[]>([]);
  const nextImage = useRef(1);
  const addImage = useCallback(
    () => setImages((was) => [...was, nextImage.current++]),
    [],
  );
  const removeImage = useCallback(
    (id: number) => setImages((was) => was.filter((each) => each !== id)),
    [],
  );

  // Only what has been filled in: a control with nothing entered says nothing.
  const summary = [
    type === "Vehicle control" ? vehicle : "",
    strain,
    images.length ? `${images.length} images` : "No images",
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
        <>
          <FieldPairs>
            <FullRow>
              <Field label="Control type" labels="value">
                {(_id, labelId) => (
                  <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                    {TYPES.map((option) => (
                      <RadioLabel key={option}>
                        <input
                          type="radio"
                          name={typeName}
                          checked={type === option}
                          onChange={() => setType(option)}
                        />
                        {option}
                      </RadioLabel>
                    ))}
                  </RadioGroup>
                )}
              </Field>
            </FullRow>

            <Field label="Vehicle used">
              {(id) => (
                <SelectInput
                  id={id}
                  value={vehicle}
                  onChange={(e) => setVehicle(e.target.value)}
                >
                  <option value="">Select vehicle used</option>
                  {VEHICLES.map((option) => (
                    <option key={option}>{option}</option>
                  ))}
                </SelectInput>
              )}
            </Field>

            <Field label="Strain / background">
              {(id) => (
                <TextInput
                  id={id}
                  value={strain}
                  onChange={(e) => setStrain(e.target.value)}
                  placeholder="e.g. AB/TL"
                />
              )}
            </Field>

            <Field label="Line description">
              {(id) => <TextInput id={id} />}
            </Field>

            <FullRow>
              <Field label="Rearing conditions" labels="value">
                {(_id, labelId) => (
                  <RadioGroup role="radiogroup" aria-labelledby={labelId}>
                    {REARING.map((option) => (
                      <RadioLabel key={option}>
                        <input
                          type="radio"
                          name={rearingName}
                          checked={rearing === option}
                          onChange={() => setRearing(option)}
                        />
                        {option}
                      </RadioLabel>
                    ))}
                  </RadioGroup>
                )}
              </Field>

              {rearing === "Not standard" && (
                <Field label="Describe">
                  {(id) => <TextArea id={id} rows={3} />}
                </Field>
              )}
            </FullRow>

            <FullRow>
              <Field label="Phenotype description">
                {(id) => <TextArea id={id} rows={3} />}
              </Field>
            </FullRow>

            <FullRow>
              <Field label="Notes">{(id) => <TextArea id={id} rows={3} />}</Field>
            </FullRow>
          </FieldPairs>

          <EntryTitle>Control images (optional)</EntryTitle>

          {images.map((id, i) => (
            <ControlImage key={id} n={i + 1} onRemove={() => removeImage(id)} />
          ))}

          <AddRowInline>
            <AddButton type="button" onClick={addImage}>
              + Add control image
            </AddButton>
          </AddRowInline>
        </>
      )}
    </EntryCard>
  );
};

/** The controls this submission was measured against. */
const ControlSection = () => {
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
        <Control
          key={id}
          n={i + 1}
          onRemove={ids.length > 1 ? () => remove(id) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={add}>
          + Add another control
        </AddButton>
      </AddRow>
    </>
  );
};

export default ControlSection;
