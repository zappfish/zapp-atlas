import { useCallback, useState, type ReactNode } from "react";
import {
  FormSectionBody,
  FormSectionBox,
  FormSectionDescription,
  FormSectionHead,
  FormSectionHeading,
  FormSectionNumber,
  FormSectionTitle,
  FormSectionToggle,
  VisuallyHidden,
} from "@/styles/elements";

/**
 * One numbered section of the form. Collapsible, so a curator can fold away
 * what they have finished and keep the rest reachable.
 */
const FormSection = ({
  slug,
  number,
  title,
  description,
  children,
}: {
  /** Anchor id, so the nav can scroll to it. */
  slug: string;
  number: number;
  title: string;
  description: string;
  children?: ReactNode;
}) => {
  const [open, setOpen] = useState(true);
  const toggle = useCallback(() => setOpen((wasOpen) => !wasOpen), []);

  return (
    <FormSectionBox id={slug}>
      <FormSectionHead>
        <FormSectionNumber>{number}</FormSectionNumber>
        <FormSectionHeading>
          <FormSectionTitle>{title}</FormSectionTitle>
          <FormSectionDescription>{description}</FormSectionDescription>
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
