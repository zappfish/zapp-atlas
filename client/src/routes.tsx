import { Navigate, Route, Routes, useParams } from "react-router";
import ChemicalDetail from "@/features/groups/ChemicalDetail";
import FishDetail from "@/features/groups/FishDetail";
import GroupView from "@/features/groups/GroupView";
import StudyDetail from "@/features/groups/StudyDetail";
import MySubmissions from "@/features/submissions/MySubmissions";
import SubmissionForm from "@/features/submissions/form/SubmissionForm";

/** A new path here also needs adding to html/client_router.py, or it 404s. */

/** Numeric params, or a redirect. NaN would reach /api as a bad request. */
const useIds = (...names: string[]): number[] | null => {
  const params = useParams();
  const ids = names.map((name) => Number(params[name]));
  return ids.every(Number.isInteger) ? ids : null;
};

const GroupRoute = () => {
  const ids = useIds("groupId");
  if (!ids) return <Navigate to="/my-submissions" replace />;
  return <GroupView groupId={ids[0]!} />;
};

const FishDetailRoute = () => {
  const ids = useIds("groupId", "entryId");
  if (!ids) return <Navigate to="/my-submissions" replace />;
  return <FishDetail groupId={ids[0]!} entryId={ids[1]!} />;
};

/** The form, which a group's page starts and its breadcrumb names. */
const GroupSubmissionRoute = () => {
  const ids = useIds("groupId");
  if (!ids) return <Navigate to="/my-submissions" replace />;
  return <SubmissionForm groupId={ids[0]!} />;
};

const ChemicalDetailRoute = () => {
  const ids = useIds("groupId", "entryId");
  if (!ids) return <Navigate to="/my-submissions" replace />;
  return <ChemicalDetail groupId={ids[0]!} entryId={ids[1]!} />;
};

const StudyDetailRoute = () => {
  const ids = useIds("groupId", "studyId");
  if (!ids) return <Navigate to="/my-submissions" replace />;
  return <StudyDetail groupId={ids[0]!} studyId={ids[1]!} />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/my-submissions" element={<MySubmissions />} />
    <Route
      path="/submissions/new"
      element={<Navigate to="/my-submissions" replace />}
    />
    <Route
      path="/research-groups/:groupId/submissions/new"
      element={<GroupSubmissionRoute />}
    />
    <Route path="/research-groups/:groupId" element={<GroupRoute />} />
    <Route
      path="/research-groups/:groupId/fish-tank/:entryId"
      element={<FishDetailRoute />}
    />
    <Route
      path="/research-groups/:groupId/chemical-cabinet/:entryId"
      element={<ChemicalDetailRoute />}
    />
    <Route
      path="/research-groups/:groupId/studies/:studyId"
      element={<StudyDetailRoute />}
    />
  </Routes>
);

export default AppRoutes;
