import { useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  useDeleteExperiment,
  useDeleteStudy,
  useGroupDashboard,
  useReplaceStudy,
  useStudy,
} from "@/api/hooks";
import type { Experiment } from "@/api/types";
import ConfirmDialog from "@/components/ConfirmDialog";
import RecordDetail from "@/components/RecordDetail";
import RecordSection, { type Row } from "@/components/RecordSection";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { EyeIcon, PencilIcon, TrashIcon } from "@/components/icons";
import { describeFish } from "@/fish";
import EditStudyForm from "./EditStudyForm";
import { ownFields } from "./studyFields";

/** An experiment goes by its fish, with how many groups of them it treated. */
const toRows = (experiments: Experiment[]): Row[] =>
  experiments.map((experiment, i) => {
    const groups = experiment.exposure_event?.length ?? 0;
    return {
      id: experiment.id,
      label: experiment.fish ? describeFish(experiment.fish) : `Experiment ${i + 1}`,
      sublabel: `${groups} exposure event${groups === 1 ? "" : "s"}`,
    };
  });

/** The study's experiments. One is opened to change it, or to add to it. */
const Experiments = ({
  groupId,
  studyId,
  experiments,
}: {
  groupId: number;
  studyId: number;
  experiments: Experiment[];
}) => {
  const [removing, setRemoving] = useState<Row | null>(null);
  const deleteExperiment = useDeleteExperiment(studyId);
  const navigate = useNavigate();
  const here = `/research-groups/${groupId}/studies/${studyId}/experiments`;
  const rows = toRows(experiments);

  const addLink = (
    <Link className="btn btn--secondary" to={`${here}/new`}>
      + New experiment
    </Link>
  );

  return (
    <>
      <RecordSection
        id="experiments"
        title="Experiments"
        rows={rows}
        emptyTitle="No experiments yet"
        emptyText="Add an experiment to describe the fish and what they were exposed to."
        emptyAction={addLink}
        // With rows, the link moves up beside the title, as on the group's page.
        actions={rows.length > 0 ? addLink : undefined}
        rowActions={(row) => (
          <RowMenu label={`Actions for ${row.label}`}>
            <RowMenuItem
              icon={<PencilIcon />}
              label="Open"
              onClick={() => navigate(`${here}/${row.id}`)}
            />
            <RowMenuItem
              icon={<TrashIcon />}
              label="Remove"
              danger
              onClick={() => setRemoving(row)}
            />
          </RowMenu>
        )}
      />

      <ConfirmDialog
        open={removing !== null}
        title="Remove experiment"
        message={`Remove ${removing?.label ?? "this experiment"}, with its exposure events and observations?`}
        isPending={deleteExperiment.isPending}
        error={deleteExperiment.error?.message}
        onConfirm={() =>
          removing &&
          deleteExperiment.mutate(removing.id, {
            onSuccess: () => setRemoving(null),
          })
        }
        onClose={() => {
          deleteExperiment.reset();
          setRemoving(null);
        }}
      />
    </>
  );
};

const StudyDetail = ({
  groupId,
  studyId,
}: {
  groupId: number;
  studyId: number;
}) => {
  const { group, members } = useGroupDashboard(groupId);
  const { isPending, error, data } = useStudy(studyId);
  const [editing, setEditing] = useState(false);
  const [removing, setRemoving] = useState(false);
  const [changingVisibility, setChangingVisibility] = useState(false);
  const deleteStudy = useDeleteStudy(groupId);
  const replaceStudy = useReplaceStudy(groupId, studyId);
  const navigate = useNavigate();

  if (error) return <p>This study is not available.</p>;

  const name = data?.nickname ?? data?.publication ?? undefined;
  // `status` says who may read the study: a draft is its group's alone.
  const isPrivate = data?.status === "draft";
  const visibilityAction = isPrivate ? "Make public" : "Make private";

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
                ...(data.annotator?.length
                  ? [
                      {
                        label: "Entered by",
                        // A member's name where the group has it, and the
                        // ORCID that was recorded otherwise.
                        value: data.annotator
                          .map(
                            (orcid) =>
                              members.find((each) => each.member === orcid)
                                ?.name ?? orcid,
                          )
                          .join(", "),
                      },
                    ]
                  : []),
                {
                  label: "Visibility",
                  value: isPrivate
                    ? "Private, visible to this group only"
                    : "Public, visible to everyone",
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
              icon={<EyeIcon />}
              label={visibilityAction}
              onClick={() => setChangingVisibility(true)}
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
        <Experiments
          groupId={groupId}
          studyId={studyId}
          experiments={data.experiment ?? []}
        />
      )}

      {data && (
        <EditStudyForm
          groupId={groupId}
          study={data}
          open={editing}
          onClose={() => setEditing(false)}
        />
      )}

      {data && (
        <ConfirmDialog
          open={changingVisibility}
          title={visibilityAction}
          message={
            isPrivate
              ? `Make ${name ?? "this study"} public? Anyone will be able to see it, with its experiments, observations and images.`
              : `Make ${name ?? "this study"} private? Only members of ${group?.name ?? "its research group"} will be able to see it.`
          }
          confirmLabel={visibilityAction}
          pendingLabel="Saving…"
          danger={false}
          isPending={replaceStudy.isPending}
          error={replaceStudy.error?.message}
          onConfirm={() =>
            replaceStudy.mutate(
              { ...ownFields(data), status: isPrivate ? "published" : "draft" },
              { onSuccess: () => setChangingVisibility(false) },
            )
          }
          onClose={() => {
            replaceStudy.reset();
            setChangingVisibility(false);
          }}
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
