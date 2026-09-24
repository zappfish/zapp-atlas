import { useCallback, useState } from "react";
import { useNavigate } from "react-router";
import type { CabinetEntry } from "@/api/groups";
import { useDeleteChemical } from "@/api/hooks";
import ConfirmDialog from "@/components/ConfirmDialog";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { EyeIcon, PencilIcon, TrashIcon } from "@/components/icons";
import AddChemicalForm from "./AddChemicalForm";
import EditChemicalForm from "./EditChemicalForm";
import RecordSection, { type Row } from "@/components/RecordSection";

// Only a chemical id for now; a name would become the label and this the sub.
const toRows = (entries: CabinetEntry[]): Row[] =>
  entries.map((entry) => ({ id: entry.id, label: entry.chemical_id }));

const RowActions = ({
  row,
  groupId,
  onEdit,
  onRemove,
}: {
  row: Row;
  groupId: number;
  onEdit: (row: Row) => void;
  onRemove: (row: Row) => void;
}) => {
  const navigate = useNavigate();

  const view = useCallback(
    () => navigate(`/research-groups/${groupId}/chemical-cabinet/${row.id}`),
    [navigate, groupId, row.id],
  );
  const edit = useCallback(() => onEdit(row), [onEdit, row]);
  const remove = useCallback(() => onRemove(row), [onRemove, row]);

  return (
    <RowMenu label={`Actions for ${row.label}`}>
      <RowMenuItem icon={<EyeIcon />} label="View details" onClick={view} />
      <RowMenuItem icon={<PencilIcon />} label="Edit" onClick={edit} />
      <RowMenuItem icon={<TrashIcon />} label="Remove" danger onClick={remove} />
    </RowMenu>
  );
};

const CabinetSection = ({
  groupId,
  entries,
  isPending,
}: {
  groupId: number;
  entries: CabinetEntry[];
  isPending: boolean;
}) => {
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<Row | null>(null);
  const [removing, setRemoving] = useState<Row | null>(null);
  const deleteChemical = useDeleteChemical(groupId);

  const confirmRemove = () => {
    if (!removing) return;
    deleteChemical.mutate(removing.id, { onSuccess: () => setRemoving(null) });
  };

  return (
    <>
      <RecordSection
        id="chemical-cabinet"
        title="Chemical Cabinet"
        rows={toRows(entries)}
        isPending={isPending}
        emptyText="Add a chemical to this group's cabinet."
        actions={
          <button
            className="btn btn--secondary"
            type="button"
            onClick={() => setAdding(true)}
          >
            + Add chemical
          </button>
        }
        rowActions={(row) => (
          <RowActions
            row={row}
            groupId={groupId}
            onEdit={setEditing}
            onRemove={setRemoving}
          />
        )}
      />

      <AddChemicalForm
        groupId={groupId}
        open={adding}
        onClose={() => setAdding(false)}
      />

      <EditChemicalForm
        groupId={groupId}
        entry={editing}
        onClose={() => setEditing(null)}
      />

      <ConfirmDialog
        open={removing !== null}
        title="Remove chemical"
        message={`Remove ${removing?.label ?? ""} from this group's cabinet?`}
        isPending={deleteChemical.isPending}
        error={deleteChemical.error?.message}
        onConfirm={confirmRemove}
        onClose={() => {
          deleteChemical.reset();
          setRemoving(null);
        }}
      />
    </>
  );
};

export default CabinetSection;
