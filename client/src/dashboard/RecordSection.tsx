import { useState } from "react";
import {
  Count,
  Empty,
  EmptyText,
  MoreButton,
  Row as RowBox,
  RowLabel,
  RowMain,
  RowSub,
  Rows,
  Section,
  SectionHead,
  SectionTitle,
  SkeletonRow,
} from "./elements";

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
const VISIBLE = 2;

const RecordRow = ({ row }: { row: Row }) => (
  <RowBox>
    <RowMain>
      <RowLabel>
        {row.label}
        {row.sublabel && <RowSub>{row.sublabel}</RowSub>}
      </RowLabel>
    </RowMain>
  </RowBox>
);

const EmptyState = ({ text }: { text: string }) => (
  <Empty>
    <EmptyText>{text}</EmptyText>
  </Empty>
);

// Holds the section's height while it loads, so arriving rows do not push the
// page down.
const Skeleton = () => (
  <Rows aria-hidden="true">
    {Array.from({ length: VISIBLE }, (_, i) => (
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
}: {
  /** Anchor id, so the sidebar's section links land here. */
  id: string;
  title: string;
  rows: Row[];
  /** Unused while pending. */
  emptyText?: string;
  isPending?: boolean;
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
      </SectionHead>

      {isPending ? (
        <Skeleton />
      ) : rows.length === 0 ? (
        <EmptyState text={emptyText ?? ""} />
      ) : (
        <>
          <Rows>
            {shown.map((row) => (
              <RecordRow key={row.id} row={row} />
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
