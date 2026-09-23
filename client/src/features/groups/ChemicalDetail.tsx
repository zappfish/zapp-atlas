import { useState } from "react";
import { useNavigate } from "react-router";
import {
  useCabinetEntry,
  useDeleteChemical,
  useGroupDashboard,
} from "@/api/hooks";
import ConfirmDialog from "@/components/ConfirmDialog";
import RecordDetail from "@/components/RecordDetail";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { PencilIcon, TrashIcon } from "@/components/icons";
import { onDate } from "@/format";
import EditChemicalForm from "./EditChemicalForm";

const ChemicalDetail = ({
  groupId,
  entryId,
}: {
  groupId: number;
  entryId: number;
}) => {
  const { group } = useGroupDashboard(groupId);
  const { isPending, error, data } = useCabinetEntry(groupId, entryId);
  const [editing, setEditing] = useState(false);
  const [removing, setRemoving] = useState(false);
  const deleteChemical = useDeleteChemical(groupId);
  const navigate = useNavigate();

  if (error) return <p>This chemical is not available.</p>;

  const confirmRemove = () =>
    deleteChemical.mutate(entryId, {
      // The record is gone, so its page is too.
      onSuccess: () =>
        navigate(`/research-groups/${groupId}#chemical-cabinet`),
    });

  return (
    <>
      <RecordDetail
        groupId={groupId}
        groupName={group?.name}
        section="chemical-cabinet"
        sectionLabel="Chemical Cabinet"
        title={data?.chemical_id}
        isPending={isPending}
        fields={
          data
            ? [
                { label: "Chemical ID", value: data.chemical_id, mono: true },
                { label: "Added on", value: onDate(data.created_at) },
              ]
            : []
        }
        actions={
          <RowMenu label={`Actions for ${data?.chemical_id ?? "this record"}`}>
            <RowMenuItem
              icon={<PencilIcon />}
              label="Edit"
              onClick={() => setEditing(true)}
            />
            <RowMenuItem
              icon={<TrashIcon />}
              label="Remove"
              danger
              onClick={() => setRemoving(true)}
            />
          </RowMenu>
        }
      />

      <EditChemicalForm
        groupId={groupId}
        entry={
          editing && data ? { id: data.id, label: data.chemical_id } : null
        }
        onClose={() => setEditing(false)}
      />

      <ConfirmDialog
        open={removing}
        title="Remove chemical"
        message={`Remove ${data?.chemical_id ?? ""} from this group's cabinet?`}
        isPending={deleteChemical.isPending}
        error={deleteChemical.error?.message}
        onConfirm={confirmRemove}
        onClose={() => {
          deleteChemical.reset();
          setRemoving(false);
        }}
      />
    </>
  );
};

export default ChemicalDetail;
