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

const RecordSection = ({
  id,
  title,
  rows,
  emptyText,
}: {
  /** Anchor id, so the sidebar's section links land here. */
  id: string;
  title: string;
  rows: Row[];
  emptyText: string;
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
          {rows.length > 0 && <Count>{rows.length}</Count>}
        </SectionTitle>
      </SectionHead>

      {rows.length === 0 ? (
        <EmptyState text={emptyText} />
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
