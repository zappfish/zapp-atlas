import {
  useCallback,
  useId,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
} from "react";
import {
  AddButton,
  AddRow,
  EntryBody,
  EntryCard,
  EntryMeta,
  FieldBox,
  FieldLabel,
  MeasureRow,
  Notes,
  NotesRemove,
  NotesToggle,
  PreviewActions,
  PreviewImage,
  RadioGroup,
  RadioLabel,
  RequiredMark,
  TextArea,
  TextInput,
  Upload,
  UploadChosen,
  UploadHint,
  UploadPane,
} from "@/styles/elements";
import Field from "../Field";

const MEASURES = [
  { label: "Scale bar", placeholder: "e.g. 100", units: ["um", "mm", "Other"] },
  { label: "Magnification", placeholder: "e.g. 40", units: ["X"] },
  { label: "Resolution", placeholder: "e.g. 300", units: ["dpi", "Other"] },
];

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

const ImageUpload = () => {
  const input = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  // Revoked where it is replaced, not on unmount: StrictMode's second render
  // would tear down the first one's effect and revoke a live URL.
  const show = useCallback((file: File | undefined) => {
    setPreview((old) => {
      if (old) URL.revokeObjectURL(old);
      return file ? URL.createObjectURL(file) : null;
    });
  }, []);

  const choose = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => show(event.target.files?.[0]),
    [show],
  );

  // preventDefault is what marks the box as a drop target; without it the
  // browser opens the file instead.
  const over = useCallback((event: DragEvent) => {
    event.preventDefault();
    setDragging(true);
  }, []);

  const leave = useCallback(() => setDragging(false), []);

  const drop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();
      setDragging(false);
      const file = event.dataTransfer.files?.[0];
      if (file?.type.startsWith("image/")) show(file);
    },
    [show],
  );

  const browse = useCallback(() => input.current?.click(), []);

  const remove = useCallback(() => {
    if (input.current) input.current.value = "";
    show(undefined);
  }, [show]);

  return (
    <Upload>
      <FieldLabel>
        Upload image
        <RequiredMark> *</RequiredMark>
      </FieldLabel>

      {preview ? (
        <UploadChosen>
          <PreviewImage src={preview} alt="" />
        </UploadChosen>
      ) : (
        <UploadPane
          isDragging={dragging}
          onClick={browse}
          onDragOver={over}
          onDragLeave={leave}
          onDrop={drop}
        >
          <UploadHint>
            Drag &amp; drop an image here, or click to browse. Accepted: .jpeg,
            .png, .tiff
          </UploadHint>
        </UploadPane>
      )}

      {/* Clipped rather than hidden, which would stop .click() opening it. */}
      <input
        className="visually-hidden"
        ref={input}
        type="file"
        accept=".jpeg,.jpg,.png,.tiff"
        onChange={choose}
      />

      {preview && (
        <PreviewActions>
          <button className="btn btn--neutral" type="button" onClick={browse}>
            Replace image
          </button>
          <button className="btn btn--neutral" type="button" onClick={remove}>
            Remove image
          </button>
        </PreviewActions>
      )}
    </Upload>
  );
};

const ImageEntry = () => {
  const [notesOpen, setNotesOpen] = useState(false);
  const openNotes = useCallback(() => setNotesOpen(true), []);
  const closeNotes = useCallback(() => setNotesOpen(false), []);

  return (
    <EntryCard>
      <EntryBody>
        <ImageUpload />

        <EntryMeta>
          {MEASURES.map((measure) => (
            <Measure key={measure.label} {...measure} />
          ))}

          <Field label="Microscope information">
            {(id) => <TextInput id={id} placeholder="Enter text" />}
          </Field>

          {notesOpen ? (
            <Notes>
              <Field label="Notes">
                {(id) => <TextArea id={id} rows={3} />}
              </Field>
              <NotesRemove type="button" onClick={closeNotes}>
                Remove notes
              </NotesRemove>
            </Notes>
          ) : (
            <NotesToggle type="button" onClick={openNotes}>
              Add notes
            </NotesToggle>
          )}
        </EntryMeta>
      </EntryBody>
    </EntryCard>
  );
};

/** Each image carries its own metadata, which may differ between them. */
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
