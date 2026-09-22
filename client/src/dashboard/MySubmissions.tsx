import { DashEyebrow, DashHeader, DashTitle } from "./elements";
import Submissions from "./Submissions";

/**
 * The caller's own submissions, across every group. No endpoint serves them
 * yet, so the list is empty.
 */
const MySubmissions = () => (
  <>
    <DashHeader>
      <div>
        <DashEyebrow>Your work</DashEyebrow>
        <DashTitle>My Submissions</DashTitle>
      </div>
    </DashHeader>

    <Submissions submissions={[]} />
  </>
);

export default MySubmissions;
