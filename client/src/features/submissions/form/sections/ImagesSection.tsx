import { useCallback, useId, useState } from "react";
import {
  AddButton,
  AddRow,
  EntryBody,
  EntryCard,
  FieldBox,
  FieldLabel,
  MeasureRow,
  NotesToggle,
  PreviewActions,
  PreviewNote,
  PreviewTitle,
  RadioGroup,
  RadioLabel,
  RequiredMark,
  TextArea,
  TextInput,
  Upload,
  UploadHint,
  UploadPane,
  UploadPreview,
} from "@/styles/elements";
import Field from "../Field";

/** A number with the unit it was measured in. */
const Measure = ({
  label,
  placeholder,
  units,
}: {
  label: string;
  placeholder: string;
  units: string[];
}) => {
  const name = useId();

  return (
    <MeasureRow>
      <Field label={label}>
        {(id) => <TextInput id={id} placeholder={placeholder} />}
      </Field>
      <FieldBox>
        <FieldLabel>Unit</FieldLabel>
        <RadioGroup>
          {units.map((unit) => (
            <RadioLabel key={unit}>
              <input type="radio" name={name} value={unit} />
              {unit}
            </RadioLabel>
          ))}
        </RadioGroup>
      </FieldBox>
    </MeasureRow>
  );
};

const ImageEntry = () => {
  const [notesOpen, setNotesOpen] = useState(false);
  const openNotes = useCallback(() => setNotesOpen(true), []);

  return (
    <EntryCard>
      <EntryBody>
        <Upload>
          <UploadPane>
            <FieldLabel>
              Upload image
              <RequiredMark aria-hidden="true"> *</RequiredMark>
            </FieldLabel>
            <TextInput type="file" accept=".jpeg,.jpg,.png,.tiff" />
            <UploadHint>
              Drag &amp; drop an image here, or click to browse. Accepted:
              .jpeg, .png, .tiff
            </UploadHint>
          </UploadPane>

          <UploadPreview>
            <PreviewTitle>Preview</PreviewTitle>
            <PreviewNote>No image selected yet.</PreviewNote>
            <PreviewActions>
              <button className="btn btn--neutral" type="button" disabled>
                Replace image
              </button>
              <button className="btn btn--neutral" type="button" disabled>
                Remove image
              </button>
            </PreviewActions>
          </UploadPreview>
        </Upload>

        <Measure
          label="Scale bar"
          placeholder="e.g. 100"
          units={["um", "mm", "Other"]}
        />
        <Measure label="Magnification" placeholder="e.g. 40" units={["X"]} />
        <Measure
          label="Resolution"
          placeholder="e.g. 300"
          units={["dpi", "Other"]}
        />

        <Field label="Microscope information">
          {(id) => <TextInput id={id} placeholder="Enter text" />}
        </Field>

        {notesOpen ? (
          <Field label="Notes">{(id) => <TextArea id={id} rows={3} />}</Field>
        ) : (
          <NotesToggle type="button" onClick={openNotes}>
            Add notes
          </NotesToggle>
        )}
      </EntryBody>
    </EntryCard>
  );
};

/**
 * The images a submission carries. Each has its own metadata, which may differ
 * between them. Layout only: nothing is stored yet.
 */
const ImagesSection = () => {
  const [count, setCount] = useState(1);
  const add = useCallback(() => setCount((was) => was + 1), []);

  return (
    <>
      {Array.from({ length: count }, (_, i) => (
        <ImageEntry key={i} />
      ))}

      <AddRow>
        <AddButton type="button" onClick={add}>
          + Upload another image
        </AddButton>
      </AddRow>
    </>
  );
};

export default ImagesSection;
