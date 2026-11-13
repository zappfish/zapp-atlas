import DashboardShell from "@/features/dashboard/DashboardShell";
import AppRoutes from "./routes";

const App = () => (
  <DashboardShell>
    <AppRoutes />
  </DashboardShell>
);

export default App;
