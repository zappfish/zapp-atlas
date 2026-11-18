import { useState } from "react";
import { useNavigate } from "react-router";
import { useDeleteFish, useFishEntry, useGroup } from "@/api/hooks";
import ConfirmDialog from "@/components/ConfirmDialog";
import RecordDetail from "@/components/RecordDetail";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { TrashIcon } from "@/components/icons";
import { describeFish, zfinStatus } from "@/fish";
import { onDate } from "@/format";

const FishDetail = ({
  groupId,
  entryId,
}: {
  groupId: number;
  entryId: number;
}) => {
  const { data: group } = useGroup(groupId);
  const { isPending, error, data } = useFishEntry(groupId, entryId);
  const [removing, setRemoving] = useState(false);
  const deleteFish = useDeleteFish(groupId);
  const navigate = useNavigate();

  if (error) return <p>This fish line is not available.</p>;

  const name = data && (data.nickname ?? describeFish(data.fish));

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
        title={name}
        badge={data?.fish.background_name ?? undefined}
        isPending={isPending}
        fields={
          data
            ? [
                { label: "Nickname", value: data.nickname ?? "—" },
                { label: "Line", value: describeFish(data.fish) },
                { label: "Background", value: data.fish.background_name ?? "—" },
                ...(data.fish.allele ?? []).map((allele, i) => ({
                  label: `Allele ${i + 1}`,
                  value: [
                    allele.allele_symbol,
                    allele.zygosity,
                    allele.alteration_type?.replace(/_/g, " "),
                    allele.affected_gene_symbol && `in ${allele.affected_gene_symbol}`,
                    allele.allele_zfin_id,
                  ]
                    .filter(Boolean)
                    .join(" · "),
                })),
                { label: "ZFIN genotype", value: zfinStatus(data.fish), mono: true },
                { label: "ZFIN fish", value: data.fish.fish_zfin_id ?? "—", mono: true },
                { label: "Notes", value: data.fish.line_description ?? "—" },
                { label: "Added on", value: onDate(data.created_at) },
              ]
            : []
        }
        actions={
          <RowMenu label={`Actions for ${name ?? "this record"}`}>
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
        message={`Remove ${name ?? ""} from this group's tank?`}
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
