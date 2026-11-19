/**
 * The controls of an image's card: the file's upload box, and the measures
 * that describe it.
 */

import {
  useCallback,
  useId,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type ReactNode,
} from "react";
import {
  FieldError,
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
import { useController } from "react-hook-form";
import Field from "./Field";
import InfoTip from "./InfoTip";
import UploadIcon from "./UploadIcon";

/** What was saved, as the number and the unit it was entered as. */
const apart = (
  saved: string,
  units: readonly string[] | undefined,
  suffix: string | undefined,
) => {
  if (suffix && saved.endsWith(suffix)) {
    return { number: saved.slice(0, -suffix.length), unit: "", other: "" };
  }
  const gap = saved.indexOf(" ");
  if (!units || gap < 0) return { number: saved, unit: "", other: "" };
  const unit = saved.slice(gap + 1);
  return units.includes(unit)
    ? { number: saved.slice(0, gap), unit, other: "" }
    : { number: saved.slice(0, gap), unit: "Other", other: unit };
};

/**
 * A number with its unit, for a slot that holds the two as one text ("100 µm",
 * "40X"). What is typed and chosen is held here, and the form is given the
 * text once there is a number.
 */
export const Measure = ({
  label,
  placeholder,
  units,
  suffix,
  name,
}: {
  label: string;
  placeholder: string;
  units?: readonly string[];
  suffix?: string;
  /** The slot the text is stored in. */
  name: string;
}) => {
  const { field } = useController({ name });
  const [entered, setEntered] = useState(() =>
    apart((field.value as string | null | undefined) ?? "", units, suffix),
  );

  const hold = (next: typeof entered) => {
    setEntered(next);
    const unit = next.unit === "Other" ? next.other.trim() : next.unit;
    const number = next.number.trim();
    field.onChange(
      number === ""
        ? null
        : suffix
          ? `${number}${suffix}`
          : unit
            ? `${number} ${unit}`
            : number,
    );
  };

  return (
    <Field label={label} name={name}>
      {(id) => (
        <MeasureRow>
          <MeasureInput>
            <TextInput
              id={id}
              placeholder={placeholder}
              value={entered.number}
              onChange={(event) => hold({ ...entered, number: event.target.value })}
              onBlur={field.onBlur}
            />
            {suffix && <MeasureSuffix>{suffix}</MeasureSuffix>}
          </MeasureInput>

          {units && (
            <RadioGroup role="radiogroup" aria-label={`${label} unit`}>
              {units.map((option) => (
                <RadioLabel key={option}>
                  <input
                    type="radio"
                    checked={entered.unit === option}
                    onChange={() => hold({ ...entered, unit: option })}
                  />
                  {option}
                </RadioLabel>
              ))}
              {/* Rendered either way, so the row does not resize when it is
                  chosen. */}
              <TextInput
                aria-label={`${label} unit`}
                placeholder="Unit"
                size={6}
                hidden={entered.unit !== "Other"}
                value={entered.other}
                onChange={(event) => hold({ ...entered, other: event.target.value })}
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

/**
 * The box a new image's file is dropped on or browsed into. The file is not
 * one of the image's fields: it is uploaded beside them, so it is handed to
 * the caller and not held in the form.
 */
export const ImageUpload = ({
  onChoose,
  error,
  info,
}: {
  onChoose: (file: File | null) => void;
  /** Why the image cannot be uploaded as it stands. */
  error?: string;
  /** Rendered in an InfoTip beside the label. */
  info?: ReactNode;
}) => {
  const message = error;
  const errorId = useId();
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
    (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      show(file);
      onChoose(file ?? null);
    },
    [show, onChoose],
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
      // Routed through the input, so a dropped file is chosen like a browsed one.
      const one = new DataTransfer();
      one.items.add(file);
      input.current.files = one.files;
      input.current.dispatchEvent(new Event("change", { bubbles: true }));
    },
    [],
  );

  const browse = useCallback(() => input.current?.click(), []);

  // Through a change event, like a drop, so the caller is told it is gone.
  const remove = useCallback(() => {
    if (!input.current) return;
    input.current.value = "";
    input.current.dispatchEvent(new Event("change", { bubbles: true }));
  }, []);

  return (
    <Upload>
      <FieldLabelRow>
        <FieldLabel>
          Upload image
          <RequiredMark> *</RequiredMark>
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
        aria-invalid={message ? true : undefined}
        aria-describedby={message ? errorId : undefined}
        ref={input}
        onChange={choose}
      />

      {message && <FieldError id={errorId}>{message}</FieldError>}

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
