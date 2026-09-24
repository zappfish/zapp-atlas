import { useCallback, useState, type ReactNode } from "react";
import {
  FormSectionBody,
  FormSectionBox,
  FormSectionHead,
  FormSectionHeading,
  FormSectionTitle,
  FormSectionToggle,
  VisuallyHidden,
} from "@/styles/elements";

/**
 * One section of the form. Collapsible, so a curator can fold away
 * what they have finished and keep the rest reachable.
 */
const FormSection = ({
  slug,
  title,
  isActive,
  children,
}: {
  /** Anchor id, so the nav can scroll to it. */
  slug: string;
  title: string;
  /** The section the nav points at. */
  isActive: boolean;
  children?: ReactNode;
}) => {
  const [open, setOpen] = useState(true);
  const toggle = useCallback(() => setOpen((wasOpen) => !wasOpen), []);

  return (
    <FormSectionBox id={slug} isOpen={open} isActive={isActive}>
      <FormSectionHead>
        <FormSectionHeading>
          <FormSectionTitle>{title}</FormSectionTitle>
        </FormSectionHeading>
        <FormSectionToggle
          type="button"
          aria-expanded={open}
          aria-controls={`${slug}-body`}
          onClick={toggle}
        >
          <span aria-hidden="true">{open ? "⌃" : "⌄"}</span>
          <VisuallyHidden>
            {open ? `Collapse ${title}` : `Expand ${title}`}
          </VisuallyHidden>
        </FormSectionToggle>
      </FormSectionHead>

      {open && (
        <FormSectionBody id={`${slug}-body`}>{children}</FormSectionBody>
      )}
    </FormSectionBox>
  );
};

export default FormSection;
