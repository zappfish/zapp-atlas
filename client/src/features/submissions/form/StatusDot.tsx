import type { SectionStatus } from "./sections";

/**
 * A section's state. Carries an error count when there is one, since "2
 * problems" is more use than "has problems".
 */
const StatusDot = ({
  status,
  errorCount,
}: {
  status: SectionStatus;
  errorCount?: number;
}) => (
  <span className={`form-dot form-dot--${status}`} aria-hidden="true">
    {status === "complete" && "✓"}
    {status === "has-errors" && errorCount}
  </span>
);

export default StatusDot;
