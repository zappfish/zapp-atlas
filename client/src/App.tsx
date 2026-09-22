import Dashboard from "./dashboard/Dashboard";

/**
 * Picks the view for the current path. Read once at mount: every client route
 * is a full page load today. A router goes in with the first in-app link.
 */
const App = () => {
  if (window.location.pathname === "/dashboard") {
    return <Dashboard />;
  }

  return (
    <main id="content">
      <p>Editing UI goes here.</p>
    </main>
  );
};

export default App;
