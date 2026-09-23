import { DashHeader, DashTitle } from "@/styles/elements";
import Submissions from "./Submissions";

/**
 * The caller's own submissions, across every group. No endpoint serves them
 * yet, so the list is empty.
 */
const MySubmissions = () => (
  <>
    <DashHeader>
      <DashTitle>My Submissions</DashTitle>
    </DashHeader>

    <Submissions
      submissions={[]}
      emptyText="Create a submission to share your observations."
    />
  </>
);

export default MySubmissions;
