import { useState, type ReactNode } from "react";
import {
  Count,
  Empty,
  EmptyText,
  MoreButton,
  RowActions,
  Row as RowBox,
  RowLabel,
  RowMain,
  RowSub,
  Rows,
  Section,
  SectionHead,
  SectionTitle,
  SectionTools,
  SkeletonRow,
} from "@/styles/elements";

/**
 * Fish tank and chemical cabinet: one component, different rows. The caller
 * maps its data to `Row`, so this knows nothing about fish or chemicals.
 */

export interface Row {
  id: number;
  label: string;
  sublabel?: string;
}

/** Rows shown before "View more". */
const VISIBLE = 4;

const RecordRow = ({ row, actions }: { row: Row; actions?: ReactNode }) => (
  <RowBox>
    <RowMain>
      <RowLabel>
        {row.label}
        {row.sublabel && <RowSub>{row.sublabel}</RowSub>}
      </RowLabel>
    </RowMain>
    {actions && <RowActions>{actions}</RowActions>}
  </RowBox>
);

const EmptyState = ({ text }: { text: string }) => (
  <Empty>
    <EmptyText>{text}</EmptyText>
  </Empty>
);

// Holds the section's height while it loads, so arriving rows do not push the
// page down. Fewer than VISIBLE, since most groups hold a handful of records
// and overshooting leaves a gap to collapse.
const SKELETON_ROWS = 2;

const Skeleton = () => (
  <Rows aria-hidden="true">
    {Array.from({ length: SKELETON_ROWS }, (_, i) => (
      <SkeletonRow key={i} />
    ))}
  </Rows>
);

const RecordSection = ({
  id,
  title,
  rows,
  emptyText,
  isPending = false,
  actions,
  rowActions,
}: {
  /** Anchor id, so the sidebar's section links land here. */
  id: string;
  title: string;
  rows: Row[];
  /** Unused while pending. */
  emptyText?: string;
  isPending?: boolean;
  /** Section-level controls, such as an add button. */
  actions?: ReactNode;
  /** A row's menu, built by the caller from the record it came from. */
  rowActions?: (row: Row) => ReactNode;
}) => {
  // The Jinja page does this with a CSS-only checkbox; here it is state.
  const [expanded, setExpanded] = useState(false);

  const hidden = rows.length - VISIBLE;
  const shown = expanded ? rows : rows.slice(0, VISIBLE);

  return (
    <Section id={id}>
      <SectionHead>
        <SectionTitle>
          {title}
          {!isPending && rows.length > 0 && <Count>{rows.length}</Count>}
        </SectionTitle>
        {actions && <SectionTools>{actions}</SectionTools>}
      </SectionHead>

      {isPending ? (
        <Skeleton />
      ) : rows.length === 0 ? (
        <EmptyState text={emptyText ?? ""} />
      ) : (
        <>
          <Rows>
            {shown.map((row) => (
              <RecordRow key={row.id} row={row} actions={rowActions?.(row)} />
            ))}
          </Rows>

          {hidden > 0 && (
            <MoreButton type="button" onClick={() => setExpanded(!expanded)}>
              {expanded ? "View less" : `View ${hidden} more`}
            </MoreButton>
          )}
        </>
      )}
    </Section>
  );
};

export default RecordSection;
