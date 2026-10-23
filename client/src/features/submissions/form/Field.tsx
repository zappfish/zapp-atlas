import { useId, type ReactNode } from "react";
import { get, useFormState, type FieldPath } from "react-hook-form";
import {
  FieldBox,
  FieldError,
  FieldHint,
  FieldLabel,
  FieldLabelRow,
  FieldValueLabel,
  RequiredMark,
} from "@/styles/elements";
import InfoTip from "./InfoTip";
import type { Submission } from "./submission";

/** Spread onto the control while it has an error. */
export type ErrorProps = {
  "aria-invalid"?: true;
  "aria-describedby"?: string;
};

/**
 * A labelled field. The id is generated and handed to the control, so callers
 * do not have to invent unique ones.
 */
const Field = ({
  label,
  required = false,
  hint,
  info,
  name,
  labels = "control",
  wide = false,
  children,
}: {
  label: string;
  required?: boolean;
  /** An example, under the control. */
  hint?: string;
  /** Rendered in an InfoTip beside the label. */
  info?: ReactNode;
  /** The validated value, whose error shows under the control. */
  name?: FieldPath<Submission>;
  /**
   * What the label describes. `<label for>` binds only to form controls, so a
   * displayed value is labelled by aria-labelledby from the other direction.
   */
  labels?: "control" | "value";
  /** Takes the whole row: a long answer, or options that need the width. */
  wide?: boolean;
  /** `labelId` is for a displayed value, which is labelled by aria-labelledby. */
  children: (id: string, labelId: string, errorProps: ErrorProps) => ReactNode;
}) => {
  const id = useId();
  const labelId = `${id}-label`;
  const errorId = `${id}-error`;
  const { errors } = useFormState<Submission>({ name });
  const message: string | undefined = name
    ? get(errors, name)?.message
    : undefined;
  const errorProps: ErrorProps = message
    ? { "aria-invalid": true, "aria-describedby": errorId }
    : {};

  const heading =
    labels === "control" ? (
      <FieldLabel id={labelId} htmlFor={id}>
        {label}
        {required && <RequiredMark aria-hidden="true"> *</RequiredMark>}
      </FieldLabel>
    ) : (
      <FieldValueLabel id={labelId}>{label}</FieldValueLabel>
    );

  return (
    <FieldBox className={wide ? "field--wide" : undefined}>
      {info ? (
        <FieldLabelRow>
          {heading}
          <InfoTip label={label}>{info}</InfoTip>
        </FieldLabelRow>
      ) : (
        heading
      )}
      {children(id, labelId, errorProps)}
      {hint && <FieldHint>{hint}</FieldHint>}
      {message && <FieldError id={errorId}>{message}</FieldError>}
    </FieldBox>
  );
};

export default Field;
