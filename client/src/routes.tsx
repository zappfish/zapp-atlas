import { Navigate, Route, Routes, useParams } from "react-router";
import ChemicalDetail from "@/features/groups/ChemicalDetail";
import FishDetail from "@/features/groups/FishDetail";
import GroupView from "@/features/groups/GroupView";
import MySubmissions from "@/features/submissions/MySubmissions";

/** Mirrors the paths the server serves the shell for (html/client_router.py). */

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

const ChemicalDetailRoute = () => {
  const ids = useIds("groupId", "entryId");
  if (!ids) return <Navigate to="/my-submissions" replace />;
  return <ChemicalDetail groupId={ids[0]!} entryId={ids[1]!} />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/my-submissions" element={<MySubmissions />} />
    <Route path="/research-groups/:groupId" element={<GroupRoute />} />
    <Route
      path="/research-groups/:groupId/fish-tank/:entryId"
      element={<FishDetailRoute />}
    />
    <Route
      path="/research-groups/:groupId/chemical-cabinet/:entryId"
      element={<ChemicalDetailRoute />}
    />
  </Routes>
);

export default AppRoutes;
