import { useMyStudies } from "@/api/hooks";
import { DashHeader, DashTitle } from "@/styles/elements";
import Submissions, { type Submission } from "./Submissions";

/** The studies of the caller's research groups, each opening its own page. */
const MySubmissions = () => {
  const { isPending, studies } = useMyStudies();

  const submissions: Submission[] = studies.map(({ study, group }) => ({
    id: study.id,
    title: study.nickname ?? study.publication ?? `Study ${study.id}`,
    status: study.status === "draft" ? "Private" : "Public",
    group: group.name,
    href: `/research-groups/${group.id}/studies/${study.id}`,
  }));

  return (
    <>
      <DashHeader>
        <DashTitle>My Submissions</DashTitle>
      </DashHeader>

      {!isPending && (
        <Submissions
          submissions={submissions}
          emptyText="Open one of your research groups to add a study."
        />
      )}
    </>
  );
};

export default MySubmissions;
