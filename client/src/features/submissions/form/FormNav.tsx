import { useCallback } from "react";
import {
  Nav,
  NavButton,
  NavHeading,
  NavLabel,
  NavLegend,
  NavList,
} from "@/styles/elements";
import StatusDot from "./StatusDot";
import {
  SECTIONS,
  STATUS_LABELS,
  type SectionSlug,
  type SectionStatus,
} from "./sections";

const NavItem = ({
  slug,
  label,
  isActive,
  onJump,
}: {
  slug: SectionSlug;
  label: string;
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
      </NavButton>
    </li>
  );
};

const Legend = () => (
  <NavLegend>
    {(Object.keys(STATUS_LABELS) as SectionStatus[]).map((status) => (
      <li key={status}>
        <StatusDot status={status} errorCount={2} />
        {STATUS_LABELS[status]}
      </li>
    ))}
  </NavLegend>
);

/**
 * The section list, with where each one stands. Jumping scrolls to a section
 * rather than hiding the others: the form is one document, and a curator
 * reads across sections while filling them.
 */
const FormNav = ({
  active,
  onJump,
}: {
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
          isActive={slug === active}
          onJump={onJump}
        />
      ))}
    </NavList>

    <NavHeading>Status</NavHeading>
    <Legend />
  </Nav>
);

export default FormNav;
