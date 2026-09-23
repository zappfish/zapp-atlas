import type { ReactNode } from "react";
import { Link } from "react-router";
import {
  Crumbs,
  CrumbSeparator,
  DashHeader,
  DashTitle,
  DetailHead,
  DetailItem,
  DetailLabel,
  DetailList,
  DetailSummary,
  DetailValue,
  RowSub,
  SkeletonText,
} from "@/styles/elements";

export interface DetailField {
  label: string;
  value: string;
  /** Identifiers read better in a monospace face. */
  mono?: boolean;
}

/**
 * One record's page: where it sits, what it is, and what can be done to it.
 * The caller supplies the fields, so this knows nothing about fish or
 * chemicals.
 */
const RecordDetail = ({
  groupId,
  groupName,
  section,
  sectionLabel,
  title,
  badge,
  fields,
  isPending,
  actions,
}: {
  groupId: number;
  groupName?: string;
  /** Anchor on the group page, e.g. "fish-tank". */
  section: string;
  sectionLabel: string;
  title?: string;
  badge?: string;
  fields: DetailField[];
  isPending: boolean;
  actions?: ReactNode;
}) => (
  <>
    <Crumbs aria-label="Breadcrumb">
      <Link to={`/research-groups/${groupId}`}>{groupName ?? "Group"}</Link>
      <CrumbSeparator aria-hidden="true">›</CrumbSeparator>
      <Link to={`/research-groups/${groupId}#${section}`}>{sectionLabel}</Link>
      <CrumbSeparator aria-hidden="true">›</CrumbSeparator>
      <span aria-current="page">
        {isPending ? <SkeletonText width="6rem" /> : title}
      </span>
    </Crumbs>

    <DashHeader>
      <DashTitle>
        {isPending ? <SkeletonText width="10rem" /> : title}
        {badge && <RowSub>{badge}</RowSub>}
      </DashTitle>
      {!isPending && actions}
    </DashHeader>

    <DetailSummary>
      <DetailList>
        <DetailHead>Details</DetailHead>
        {isPending ? (
          <DetailItem>
            <SkeletonText width="14rem" />
          </DetailItem>
        ) : (
          fields.map((field) => (
            <DetailItem key={field.label}>
              <DetailLabel>{field.label}</DetailLabel>
              <DetailValue
                className={field.mono ? "detail-item__value--mono" : undefined}
              >
                {field.value}
              </DetailValue>
            </DetailItem>
          ))
        )}
      </DetailList>
    </DetailSummary>
  </>
);

export default RecordDetail;
