import type { ReactNode } from "react";
import { DashMain, DashboardLayout } from "./elements";
import Sidebar from "./Sidebar";
import "./dashboard.css";

/**
 * Layout for every signed-in page: the sidebar, and a panel the route fills.
 * Holds no data of its own — Sidebar fetches the group list, and whatever
 * renders as children fetches its own.
 */
const DashboardShell = ({ children }: { children: ReactNode }) => (
  <DashboardLayout>
    <Sidebar />
    <DashMain>{children}</DashMain>
  </DashboardLayout>
);

export default DashboardShell;
