import { Navigate, Route, Routes, useParams } from "react-router";
import GroupView from "@/features/groups/GroupView";
import MySubmissions from "@/features/submissions/MySubmissions";

/** Mirrors the paths the server serves the shell for (html/client_router.py). */

const GroupRoute = () => {
  const { groupId } = useParams();
  const id = Number(groupId);
  // NaN if the URL is malformed; the server checks its own entry point.
  if (!Number.isInteger(id)) return <Navigate to="/my-submissions" replace />;
  return <GroupView groupId={id} />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/my-submissions" element={<MySubmissions />} />
    <Route path="/research-groups/:groupId" element={<GroupRoute />} />
  </Routes>
);

export default AppRoutes;
