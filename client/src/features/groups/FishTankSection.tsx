import { useState } from "react";
import type { FishTankEntry } from "@/api/groups";
import { useDeleteFish } from "@/api/hooks";
import ConfirmDialog from "@/components/ConfirmDialog";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { EyeIcon, TrashIcon } from "@/components/icons";
import AddFishForm from "./AddFishForm";
import RecordSection, { type Row } from "@/components/RecordSection";

const toRows = (entries: FishTankEntry[]): Row[] =>
  entries.map((entry) => ({
    id: entry.id,
    label: entry.fish.name,
    sublabel: entry.fish.zfin_id,
  }));

const FishTankSection = ({
  groupId,
  entries,
  isPending,
}: {
  groupId: number;
  entries: FishTankEntry[];
  isPending: boolean;
}) => {
  const [adding, setAdding] = useState(false);
  const [removing, setRemoving] = useState<Row | null>(null);
  const deleteFish = useDeleteFish(groupId);

  const confirmRemove = () => {
    if (!removing) return;
    deleteFish.mutate(removing.id, { onSuccess: () => setRemoving(null) });
  };

  return (
    <>
      <RecordSection
        id="fish-tank"
        title="Fish Tank"
        rows={toRows(entries)}
        isPending={isPending}
        emptyText="Add a fish line to start building this group's tank."
        actions={
          <button
            className="btn btn--secondary"
            type="button"
            onClick={() => setAdding(true)}
          >
            + Add fish
          </button>
        }
        rowActions={(row) => (
          <RowMenu label={`Actions for ${row.label}`}>
            {/* Detail pages are not built yet. */}
            <RowMenuItem icon={<EyeIcon />} label="View details" disabled />
            <RowMenuItem
              icon={<TrashIcon />}
              label="Remove"
              danger
              onClick={() => setRemoving(row)}
            />
          </RowMenu>
        )}
      />

      <AddFishForm
        groupId={groupId}
        open={adding}
        onClose={() => setAdding(false)}
      />

      <ConfirmDialog
        open={removing !== null}
        title="Remove fish line"
        message={`Remove ${removing?.label ?? ""} from this group's tank?`}
        isPending={deleteFish.isPending}
        error={deleteFish.error?.message}
        onConfirm={confirmRemove}
        onClose={() => {
          deleteFish.reset();
          setRemoving(null);
        }}
      />
    </>
  );
};

export default FishTankSection;
