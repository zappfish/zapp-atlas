import { useCallback } from "react";
import {
  Nav,
  NavButton,
  NavHeading,
  NavLabel,
  NavList,
} from "@/styles/elements";
import StatusDot from "./StatusDot";
import {
  SECTIONS,
  type SectionSlug,
  type SectionStatus,
} from "./sections";

const NavItem = ({
  slug,
  label,
  status,
  isActive,
  onJump,
}: {
  slug: SectionSlug;
  label: string;
  status: SectionStatus;
  isActive: boolean;
  onJump: (slug: SectionSlug) => void;
}) => {
  const jump = useCallback(() => onJump(slug), [onJump, slug]);

  return (
    <li>
      <NavButton
        isActive={isActive}
        type="button"
        aria-current={isActive ? "step" : undefined}
        onClick={jump}
      >
        <NavLabel>{label}</NavLabel>
        <StatusDot status={status} />
      </NavButton>
    </li>
  );
};

/**
 * The section list, with where each one stands. Jumping scrolls to a section
 * rather than hiding the others: the form is one document, and a curator
 * reads across sections while filling them.
 */
const FormNav = ({
  statuses,
  active,
  onJump,
}: {
  statuses: Record<SectionSlug, SectionStatus>;
  active: SectionSlug;
  onJump: (slug: SectionSlug) => void;
}) => (
  <Nav>
    <NavHeading>Form sections</NavHeading>
    <NavList>
      {SECTIONS.map(({ slug, label }) => (
        <NavItem
          key={slug}
          slug={slug}
          label={label}
          status={statuses[slug]}
          isActive={slug === active}
          onJump={onJump}
        />
      ))}
    </NavList>
  </Nav>
);

export default FormNav;
