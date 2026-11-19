import { useState } from "react";
import { useNavigate } from "react-router";
import { useDeleteStudy, useGroupDashboard, useStudy } from "@/api/hooks";
import ConfirmDialog from "@/components/ConfirmDialog";
import RecordDetail from "@/components/RecordDetail";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { PencilIcon, TrashIcon } from "@/components/icons";
import EditStudyForm from "./EditStudyForm";

const StudyDetail = ({
  groupId,
  studyId,
}: {
  groupId: number;
  studyId: number;
}) => {
  const { group } = useGroupDashboard(groupId);
  const { isPending, error, data } = useStudy(studyId);
  const [editing, setEditing] = useState(false);
  const [removing, setRemoving] = useState(false);
  const deleteStudy = useDeleteStudy(groupId);
  const navigate = useNavigate();

  if (error) return <p>This study is not available.</p>;

  const name = data?.nickname ?? data?.publication ?? undefined;

  const confirmRemove = () =>
    deleteStudy.mutate(studyId, {
      onSuccess: () => navigate(`/research-groups/${groupId}#studies`),
    });

  return (
    <>
      <RecordDetail
        groupId={groupId}
        groupName={group?.name}
        section="studies"
        sectionLabel="Studies"
        title={name}
        isPending={isPending}
        fields={
          data
            ? [
                {
                  label: "Publication",
                  value: data.publication ?? "Unpublished",
                  mono: Boolean(data.publication),
                },
                ...(data.nickname
                  ? [{ label: "Nickname", value: data.nickname }]
                  : []),
                ...(data.description
                  ? [{ label: "Description", value: data.description }]
                  : []),
                ...(data.lab ? [{ label: "ZFIN lab", value: data.lab, mono: true }] : []),
                {
                  label: "Visibility",
                  value:
                    data.status === "draft"
                      ? "Draft, visible to this group only"
                      : "Published",
                },
              ]
            : []
        }
        actions={
          <RowMenu label={`Actions for ${name ?? "this study"}`}>
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

      {data && (
        <EditStudyForm
          groupId={groupId}
          study={data}
          open={editing}
          onClose={() => setEditing(false)}
        />
      )}

      <ConfirmDialog
        open={removing}
        title="Remove study"
        message={`Remove ${name ?? "this study"} from this group?`}
        isPending={deleteStudy.isPending}
        error={deleteStudy.error?.message}
        onConfirm={confirmRemove}
        onClose={() => {
          deleteStudy.reset();
          setRemoving(false);
        }}
      />
    </>
  );
};

export default StudyDetail;
