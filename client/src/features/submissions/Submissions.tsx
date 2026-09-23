import { useState } from "react";
import {
  Count,
  Empty,
  EmptyText,
  EmptyTitle,
  MetaSeparator,
  Status,
  StatusDot,
  SubmissionInfo,
  SubmissionItem,
  SubmissionList,
  SubmissionMeta,
  SubmissionTitle,
  SubmissionTools,
  SubmissionsHead,
  SubmissionsSection,
  SubmissionsTitle,
  SubmittedBy,
  Tab,
  TabCount,
  TabList,
  UpdatedOn,
} from "@/styles/elements";
/**
 * A group's submissions, filtered by status. The Jinja page's tabs are inert;
 * here the selection is state, so they filter.
 *
 * No endpoint serves submissions yet, so the list is always empty. The shape
 * is the one the Jinja page assumes.
 */

/** Not in the schema; the set the Jinja filter tabs assume. */
export const STATUSES = [
  "Published",
  "In Progress",
  "On Hold",
  "Retracted",
] as const;

export type StatusName = (typeof STATUSES)[number];

export interface Submission {
  id: number;
  title: string;
  status: StatusName;
  submittedBy: string;
  date: string;
}

type Filter = StatusName | "All";

const FILTERS: Filter[] = ["All", ...STATUSES];

const FilterTabs = ({
  submissions,
  active,
  onSelect,
}: {
  submissions: Submission[];
  active: Filter;
  onSelect: (filter: Filter) => void;
}) => {
  const count = (filter: Filter) =>
    filter === "All"
      ? submissions.length
      : submissions.filter((s) => s.status === filter).length;

  return (
    <TabList>
      {FILTERS.map((filter) => {
        const n = count(filter);
        return (
          <Tab
            key={filter}
            type="button"
            isActive={filter === active}
            aria-pressed={filter === active}
            onClick={() => onSelect(filter)}
          >
            {filter}
            {/* Zero is shown on All only, where it means "none at all". */}
            {(n > 0 || filter === "All") && <TabCount>{n}</TabCount>}
          </Tab>
        );
      })}
    </TabList>
  );
};

const SubmissionRow = ({ submission }: { submission: Submission }) => (
  <SubmissionItem>
    <SubmissionInfo>
      <SubmissionTitle>{submission.title}</SubmissionTitle>
      <SubmissionMeta>
        <Status status={submission.status}>
          <StatusDot aria-hidden="true" />
          {submission.status}
        </Status>
        <MetaSeparator aria-hidden="true">&middot;</MetaSeparator>
        <SubmittedBy>Submitted by {submission.submittedBy}</SubmittedBy>
        <MetaSeparator aria-hidden="true">&middot;</MetaSeparator>
        <UpdatedOn>Updated on {submission.date}</UpdatedOn>
      </SubmissionMeta>
    </SubmissionInfo>
  </SubmissionItem>
);

const Submissions = ({ submissions }: { submissions: Submission[] }) => {
  const [filter, setFilter] = useState<Filter>("All");

  const shown =
    filter === "All"
      ? submissions
      : submissions.filter((s) => s.status === filter);

  return (
    <SubmissionsSection id="submissions">
      <SubmissionsHead>
        <SubmissionsTitle>
          Submissions
          {submissions.length > 0 && <Count>{submissions.length}</Count>}
        </SubmissionsTitle>
      </SubmissionsHead>

      {submissions.length > 0 && (
        <SubmissionTools>
          <FilterTabs
            submissions={submissions}
            active={filter}
            onSelect={setFilter}
          />
        </SubmissionTools>
      )}

      <SubmissionList>
        {shown.map((submission) => (
          <SubmissionRow key={submission.id} submission={submission} />
        ))}
      </SubmissionList>

      {shown.length === 0 && (
        <Empty>
          <EmptyTitle>
            {submissions.length === 0
              ? "No submissions yet"
              : `No ${filter.toLowerCase()} submissions`}
          </EmptyTitle>
          <EmptyText>
            {submissions.length === 0
              ? "Create a submission to share this group's observations."
              : "Try another status."}
          </EmptyText>
        </Empty>
      )}
    </SubmissionsSection>
  );
};

export default Submissions;
