import { useId, type ReactNode } from "react";
import {
  FieldBox,
  FieldHint,
  FieldLabel,
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
  children,
}: {
  label: string;
  required?: boolean;
  /** An example, under the control. */
  hint?: string;
  children: (id: string) => ReactNode;
}) => {
  const id = useId();

  return (
    <FieldBox>
      <FieldLabel htmlFor={id}>
        {label}
        {required && <RequiredMark aria-hidden="true"> *</RequiredMark>}
      </FieldLabel>
      {children(id)}
      {hint && <FieldHint>{hint}</FieldHint>}
    </FieldBox>
  );
};

export default Field;
