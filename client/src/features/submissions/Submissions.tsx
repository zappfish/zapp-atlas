import { useState } from "react";
import { Link } from "react-router";
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
} from "@/styles/elements";

/** What has been entered, filtered by who can see it. */

/** A study's `status`, as it is shown. */
export const STATUSES = ["Draft", "Published"] as const;

export type StatusName = (typeof STATUSES)[number];

export interface Submission {
  id: number;
  title: string;
  status: StatusName;
  /** The research group it belongs to. */
  group: string;
  /** Its own page. */
  href: string;
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
      <SubmissionTitle>
        <Link to={submission.href}>{submission.title}</Link>
      </SubmissionTitle>
      <SubmissionMeta>
        <Status status={submission.status}>
          <StatusDot aria-hidden="true" />
          {submission.status}
        </Status>
        <MetaSeparator aria-hidden="true">&middot;</MetaSeparator>
        <SubmittedBy>{submission.group}</SubmittedBy>
      </SubmissionMeta>
    </SubmissionInfo>
  </SubmissionItem>
);

const Submissions = ({
  submissions,
  emptyText,
}: {
  submissions: Submission[];
  /** What to do about there being none. */
  emptyText: string;
}) => {
  const [filter, setFilter] = useState<Filter>("All");

  const shown =
    filter === "All"
      ? submissions
      : submissions.filter((s) => s.status === filter);

  return (
    <SubmissionsSection id="submissions">
      <SubmissionsHead>
        <SubmissionsTitle>
          Studies
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
              ? "No studies yet"
              : `No ${filter.toLowerCase()} studies`}
          </EmptyTitle>
          <EmptyText>
            {submissions.length === 0 ? emptyText : "Try another status."}
          </EmptyText>
        </Empty>
      )}
    </SubmissionsSection>
  );
};

export default Submissions;
