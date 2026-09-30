import { useId, type ReactNode } from "react";
import {
  FieldBox,
  FieldHint,
  FieldLabel,
  FieldValueLabel,
  RequiredMark,
} from "@/styles/elements";

/**
 * A labelled field. The id is generated and handed to the control, so callers
 * do not have to invent unique ones.
 */
const Field = ({
  label,
  required = false,
  hint,
  labels = "control",
  wide = false,
  children,
}: {
  label: string;
  required?: boolean;
  /** An example, under the control. */
  hint?: string;
  /**
   * What the label describes. `<label for>` binds only to form controls, so a
   * displayed value is labelled by aria-labelledby from the other direction.
   */
  labels?: "control" | "value";
  /** Takes the whole row: a long answer, or options that need the width. */
  wide?: boolean;
  /** `labelId` is for a displayed value, which is labelled by aria-labelledby. */
  children: (id: string, labelId: string) => ReactNode;
}) => {
  const id = useId();
  const labelId = `${id}-label`;

  return (
    <FieldBox className={wide ? "field--wide" : undefined}>
      {labels === "control" ? (
        <FieldLabel id={labelId} htmlFor={id}>
          {label}
          {required && <RequiredMark aria-hidden="true"> *</RequiredMark>}
        </FieldLabel>
      ) : (
        <FieldValueLabel id={labelId}>{label}</FieldValueLabel>
      )}
      {children(id, labelId)}
      {hint && <FieldHint>{hint}</FieldHint>}
    </FieldBox>
  );
};

export default Field;
