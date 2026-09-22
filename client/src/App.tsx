import DashboardShell from "./dashboard/DashboardShell";
import GroupView from "./dashboard/GroupView";
import MySubmissions from "./dashboard/MySubmissions";

/**
 * Picks the view for the current path. Read once at mount: every client route
 * is a full page load today. A router goes in with the first in-app link.
 */
const App = () => {
  const { pathname } = window.location;

  const group = pathname.match(/^\/research-groups\/(\d+)$/);
  if (group) {
    return (
      <DashboardShell>
        <GroupView groupId={Number(group[1])} />
      </DashboardShell>
    );
  }

  if (pathname === "/my-submissions") {
    return (
      <DashboardShell>
        <MySubmissions />
      </DashboardShell>
    );
  }

  return (
    <main id="content">
      <p>Editing UI goes here.</p>
    </main>
  );
};

export default App;
