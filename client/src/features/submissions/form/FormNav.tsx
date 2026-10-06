import { useCallback } from "react";
import {
  Nav,
  NavButton,
  NavHeading,
  NavHelp,
  NavHelpText,
  NavHelpTitle,
  NavLabel,
  NavList,
  NavProgress,
  NavProgressCount,
  NavProgressFill,
  NavProgressHead,
  NavProgressPercent,
  NavProgressTrack,
  NavStep,
} from "@/styles/elements";
import StatusDot from "./StatusDot";
import { SECTIONS, type SectionSlug, type SectionStatus } from "./sections";

const NavItem = ({
  slug,
  label,
  step,
  status,
  isActive,
  onJump,
}: {
  slug: SectionSlug;
  label: string;
  step: number;
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
        {/* The number stands in for the dot until the section is finished. */}
        {status === "complete" ? (
          <StatusDot status={status} />
        ) : (
          <NavStep aria-hidden="true">{step}</NavStep>
        )}
        <NavLabel>{label}</NavLabel>
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
  complete,
  active,
  onJump,
}: {
  statuses: Record<SectionSlug, SectionStatus>;
  complete: number;
  active: SectionSlug;
  onJump: (slug: SectionSlug) => void;
}) => {
  const percent = Math.round((complete / SECTIONS.length) * 100);

  return (
    <Nav>
      <NavHeading>Submission progress</NavHeading>

      <NavProgress>
        <NavProgressHead>
          <NavProgressCount>
            {complete} of {SECTIONS.length} complete
          </NavProgressCount>
          <NavProgressPercent>{percent}%</NavProgressPercent>
        </NavProgressHead>
        <NavProgressTrack
          role="progressbar"
          aria-valuenow={complete}
          aria-valuemin={0}
          aria-valuemax={SECTIONS.length}
          aria-label="Sections complete"
        >
          <NavProgressFill style={{ width: `${percent}%` }} />
        </NavProgressTrack>
      </NavProgress>

      <NavList>
        {SECTIONS.map(({ slug, label }, i) => (
          <NavItem
            key={slug}
            slug={slug}
            label={label}
            step={i + 1}
            status={statuses[slug]}
            isActive={slug === active}
            onJump={onJump}
          />
        ))}
      </NavList>

      <NavHelp>
        <NavHelpTitle>Need help?</NavHelpTitle>
        <NavHelpText>
          Review the submission guide or contact our data team.
        </NavHelpText>
        <a href="/curation-guidelines">View submission guide</a>
      </NavHelp>
    </Nav>
  );
};

export default FormNav;
