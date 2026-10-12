/**
 * An image and the metadata that describes it, shared by the Images section and
 * by a control's optional images.
 */

import {
  useCallback,
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
import { useFormContext, type FieldPath } from "react-hook-form";
import Field from "./Field";
import type { Submission } from "./submission";
import UploadIcon from "./UploadIcon";

export const Measure = ({
  label,
  placeholder,
  units,
  suffix,
  name,
  unitName,
}: {
  label: string;
  placeholder: string;
  units?: readonly string[];
  suffix?: string;
  name: FieldPath<Submission>;
  unitName: FieldPath<Submission>;
}) => {
  const { register, watch } = useFormContext<Submission>();
  const unit = watch(unitName);

  return (
    <>
      <Field label={label}>
        {(id) => (
          <MeasureInput>
            <TextInput id={id} placeholder={placeholder} {...register(name)} />
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
                <input type="radio" value={option} {...register(unitName)} />
                {option}
              </RadioLabel>
            ))}
            {/* Registered apart from the radios, which hold "Other" itself. */}
            {unit === "Other" && (
              <TextInput
                aria-label={`${label} unit`}
                placeholder="Unit"
                size={6}
                {...register(`${unitName}Other` as FieldPath<Submission>)}
              />
            )}
          </RadioGroup>
        </FieldBox>
      )}
    </>
  );
};

export const ImageUpload = ({
  name,
  required = true,
}: {
  name: FieldPath<Submission>;
  required?: boolean;
}) => {
  const { register } = useFormContext<Submission>();
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
          <UploadIcon />
          <UploadHint>Drag &amp; drop an image here, or click to browse.</UploadHint>
          <UploadLimits>JPG, PNG or TIFF, up to 50MB.</UploadLimits>
        </UploadPane>
      )}

      {/* Clipped rather than hidden, which would stop .click() opening it. */}
      <input
        className="visually-hidden"
        type="file"
        accept=".jpeg,.jpg,.png,.tiff"
        {...register(name)}
        ref={(node) => {
          register(name).ref(node);
          input.current = node;
        }}
        onChange={(event) => {
          void register(name).onChange(event);
          choose(event);
        }}
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
