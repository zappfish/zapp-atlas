import { useState } from "react";
import { useNavigate } from "react-router";
import { useDeleteFish, useFishEntry, useGroupDashboard } from "@/api/hooks";
import ConfirmDialog from "@/components/ConfirmDialog";
import RecordDetail from "@/components/RecordDetail";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { TrashIcon } from "@/components/icons";
import { onDate } from "@/format";

const FishDetail = ({
  groupId,
  entryId,
}: {
  groupId: number;
  entryId: number;
}) => {
  const { group } = useGroupDashboard(groupId);
  const { isPending, error, data } = useFishEntry(groupId, entryId);
  const [removing, setRemoving] = useState(false);
  const deleteFish = useDeleteFish(groupId);
  const navigate = useNavigate();

  if (error) return <p>This fish line is not available.</p>;

  const confirmRemove = () =>
    deleteFish.mutate(entryId, {
      // The record is gone, so its page is too.
      onSuccess: () => navigate(`/research-groups/${groupId}#fish-tank`),
    });

  return (
    <>
      <RecordDetail
        groupId={groupId}
        groupName={group?.name}
        section="fish-tank"
        sectionLabel="Fish Tank"
        title={data?.fish.name}
        badge={data?.fish.zfin_id}
        isPending={isPending}
        fields={
          data
            ? [
                { label: "Name", value: data.fish.name },
                { label: "ZFIN ID", value: data.fish.zfin_id, mono: true },
                { label: "Added on", value: onDate(data.created_at) },
              ]
            : []
        }
        actions={
          <RowMenu label={`Actions for ${data?.fish.name ?? "this record"}`}>
            <RowMenuItem
              icon={<TrashIcon />}
              label="Remove"
              danger
              onClick={() => setRemoving(true)}
            />
          </RowMenu>
        }
      />

      <ConfirmDialog
        open={removing}
        title="Remove fish line"
        message={`Remove ${data?.fish.name ?? ""} from this group's tank?`}
        isPending={deleteFish.isPending}
        error={deleteFish.error?.message}
        onConfirm={confirmRemove}
        onClose={() => {
          deleteFish.reset();
          setRemoving(false);
        }}
      />
    </>
  );
};

export default FishDetail;
