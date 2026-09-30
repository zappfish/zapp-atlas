/**
 * An image and the metadata that describes it, shared by the Images section and
 * by a control's optional images.
 */

import {
  useCallback,
  useId,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
} from "react";
import {
  FieldBox,
  FieldLabel,
  MeasureInput,
  MeasureSuffix,
  PreviewActions,
  PreviewImage,
  RadioGroup,
  RadioLabel,
  RequiredMark,
  TextInput,
  Upload,
  UploadChosen,
  UploadHint,
  UploadLimits,
  UploadPane,
} from "@/styles/elements";
import Field from "./Field";

export const Measure = ({
  label,
  placeholder,
  units,
  suffix,
}: {
  label: string;
  placeholder: string;
  units?: string[];
  suffix?: string;
}) => {
  const name = useId();
  const [unit, setUnit] = useState("");

  return (
    <>
      <Field label={label}>
        {(id) => (
          <MeasureInput>
            <TextInput id={id} placeholder={placeholder} />
            {suffix && <MeasureSuffix>{suffix}</MeasureSuffix>}
          </MeasureInput>
        )}
      </Field>
      {units && (
        <FieldBox>
          <FieldLabel>Unit</FieldLabel>
          <RadioGroup>
            {units.map((option) => (
              <RadioLabel key={option}>
                <input
                  type="radio"
                  name={name}
                  value={option}
                  checked={unit === option}
                  onChange={() => setUnit(option)}
                />
                {option}
              </RadioLabel>
            ))}
            {/* "Other" says the unit is none of the above; this says what. */}
            {unit === "Other" && (
              <TextInput
                aria-label={`${label} unit`}
                placeholder="Unit"
                size={6}
              />
            )}
          </RadioGroup>
        </FieldBox>
      )}
    </>
  );
};

export const ImageUpload = ({
  required = true,
}: {
  required?: boolean;
} = {}) => {
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
        {required && <RequiredMark> *</RequiredMark>}
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
          <UploadHint>Drag &amp; drop an image here, or click to browse.</UploadHint>
          <UploadLimits>JPG, PNG or TIFF, up to 50MB.</UploadLimits>
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
