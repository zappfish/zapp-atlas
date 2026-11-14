import { useCallback, useState } from "react";
import { useNavigate } from "react-router";
import { useGroupStudies } from "@/api/hooks";
import type { StudySummary } from "@/api/types";
import RecordSection, { type Row } from "@/components/RecordSection";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { EyeIcon } from "@/components/icons";
import AddStudyForm from "./AddStudyForm";

/** A study goes by its nickname when it has one, and its publication otherwise. */
const toRows = (studies: StudySummary[]): Row[] =>
  studies.map((study) => ({
    id: study.id,
    label: study.nickname ?? study.publication ?? `Study ${study.id}`,
    sublabel: study.nickname ? (study.publication ?? undefined) : undefined,
  }));

const RowActions = ({ row, groupId }: { row: Row; groupId: number }) => {
  const navigate = useNavigate();
  const view = useCallback(
    () => navigate(`/research-groups/${groupId}/studies/${row.id}`),
    [navigate, groupId, row.id],
  );

  return (
    <RowMenu label={`Actions for ${row.label}`}>
      <RowMenuItem icon={<EyeIcon />} label="View details" onClick={view} />
    </RowMenu>
  );
};

/** The group's studies. Adding one opens its page; removing is done there. */
const StudiesSection = ({ groupId }: { groupId: number }) => {
  const [adding, setAdding] = useState(false);
  const studies = useGroupStudies(groupId);
  const rows = toRows(studies.data ?? []);

  const addButton = (
    <button
      className="btn btn--secondary"
      type="button"
      onClick={() => setAdding(true)}
    >
      + New study
    </button>
  );

  return (
    <>
      <RecordSection
        id="studies"
        title="Studies"
        rows={rows}
        isPending={studies.isPending}
        error={studies.error}
        onRetry={() => void studies.refetch()}
        emptyTitle="No studies yet"
        emptyText="Add a study to group this lab's submissions under it."
        emptyAction={addButton}
        // With rows, the button moves up beside the title, as in the fish
        // tank; in the empty box it would otherwise appear twice.
        actions={rows.length > 0 ? addButton : undefined}
        rowActions={(row) => <RowActions row={row} groupId={groupId} />}
      />

      <AddStudyForm
        groupId={groupId}
        open={adding}
        onClose={() => setAdding(false)}
      />
    </>
  );
};

export default StudiesSection;
