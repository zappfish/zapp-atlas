import { useQuery } from "@tanstack/react-query";
import { fetchGroups } from "@/api/groups";
import { keys } from "@/api/queries";
import Dashboard, { DashboardSkeleton } from "./dashboard/Dashboard";

/**
 * Picks the view for the current path. Read once at mount: every client route
 * is a full page load today. A router goes in with the first in-app link.
 */

/**
 * /dashboard names no group, so it opens the caller's first one. The group
 * pages under /research-groups/{id} will pass an id instead.
 */
const FirstGroupDashboard = () => {
  const { isPending, error, data } = useQuery({
    queryKey: keys.groups,
    queryFn: ({ signal }) => fetchGroups(signal),
  });

  // The group id is the one thing the dashboard cannot render without, so
  // this wait is the page's shell rather than a section's placeholder.
  if (isPending) return <DashboardSkeleton />;
  if (error) return <p>Could not load your research groups.</p>;

  const [first] = data;
  if (!first) return <p>You are not in a research group yet.</p>;

  return <Dashboard groupId={first.id} />;
};

const App = () => {
  if (window.location.pathname === "/dashboard") {
    return <FirstGroupDashboard />;
  }

  return (
    <main id="content">
      <p>Editing UI goes here.</p>
    </main>
  );
};

export default App;
