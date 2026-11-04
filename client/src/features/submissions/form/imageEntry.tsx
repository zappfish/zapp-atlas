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
  type ReactNode,
} from "react";
import {
  FieldLabel,
  FieldLabelRow,
  MeasureRow,
  MeasureInput,
  MeasureSuffix,
  PreviewAction,
  PreviewActions,
  PreviewRemove,
  PreviewImage,
  RadioGroup,
  RadioLabel,
  RequiredMark,
  TextInput,
  Upload,
  UploadChosen,
  UploadFile,
  UploadFileName,
  UploadHint,
  UploadLimits,
  UploadPane,
} from "@/styles/elements";
import { useFormContext, type FieldPath } from "react-hook-form";
import Field from "./Field";
import InfoTip from "./InfoTip";
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
    <Field label={label}>
      {(id) => (
        <MeasureRow>
          <MeasureInput>
            <TextInput id={id} placeholder={placeholder} {...register(name)} />
            {suffix && <MeasureSuffix>{suffix}</MeasureSuffix>}
          </MeasureInput>

          {units && (
            <RadioGroup
              role="radiogroup"
              aria-label={`${label} unit`}
            >
              {units.map((option) => (
                <RadioLabel key={option}>
                  <input type="radio" value={option} {...register(unitName)} />
                  {option}
                </RadioLabel>
              ))}
              {/* Rendered either way, so the row does not resize when it is
                  chosen. Registered apart from the radios, which hold
                  "Other" itself. */}
              <TextInput
                aria-label={`${label} unit`}
                placeholder="Unit"
                size={6}
                hidden={unit !== "Other"}
                {...register(`${unitName}Other` as FieldPath<Submission>)}
              />
            </RadioGroup>
          )}
        </MeasureRow>
      )}
    </Field>
  );
};

interface Preview {
  url: string;
  name: string;
  size: number;
  /** <img> renders TIFF only in Safari. */
  isTiff: boolean;
}

/** Extension fallback: some OSes report .tif with an empty MIME type. */
const isTiff = (file: File) =>
  file.type === "image/tiff" || /\.tiff?$/i.test(file.name);

const megabytes = (bytes: number) => `${(bytes / 1024 / 1024).toFixed(1)} MB`;

export const ImageUpload = ({
  name,
  required = true,
  info,
}: {
  name: FieldPath<Submission>;
  required?: boolean;
  /** Rendered in an InfoTip beside the label. */
  info?: ReactNode;
}) => {
  const { register } = useFormContext<Submission>();
  const input = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [dragging, setDragging] = useState(false);

  // Revoked where it is replaced, not on unmount: StrictMode's second render
  // would tear down the first one's effect and revoke a live URL.
  const show = useCallback((file: File | undefined) => {
    setPreview((old) => {
      if (old) URL.revokeObjectURL(old.url);
      return file
        ? {
            url: URL.createObjectURL(file),
            name: file.name,
            size: file.size,
            isTiff: isTiff(file),
          }
        : null;
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
      if (!input.current || !file) return;
      if (!file.type.startsWith("image/") && !isTiff(file)) return;
      // Routed through the input so RHF registers it like a browsed file.
      const one = new DataTransfer();
      one.items.add(file);
      input.current.files = one.files;
      input.current.dispatchEvent(new Event("change", { bubbles: true }));
    },
    [],
  );

  const browse = useCallback(() => input.current?.click(), []);

  const remove = useCallback(() => {
    if (input.current) input.current.value = "";
    show(undefined);
  }, [show]);

  return (
    <Upload>
      <FieldLabelRow>
        <FieldLabel>
          Upload image
          {required && <RequiredMark> *</RequiredMark>}
        </FieldLabel>
        {info && <InfoTip label="Upload image">{info}</InfoTip>}
      </FieldLabelRow>

      {preview ? (
        <UploadChosen>
          {preview.isTiff ? (
            <UploadFile>
              <UploadFileName>{preview.name}</UploadFileName>
              <UploadLimits>
                {megabytes(preview.size)} · TIFF images are not previewed
              </UploadLimits>
            </UploadFile>
          ) : (
            <PreviewImage src={preview.url} alt="" />
          )}
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
        accept=".jpeg,.jpg,.png,.tif,.tiff"
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
          <PreviewAction type="button" onClick={browse}>
            Replace image
          </PreviewAction>
          <PreviewRemove type="button" onClick={remove}>
            Remove
          </PreviewRemove>
        </PreviewActions>
      )}
    </Upload>
  );
};
