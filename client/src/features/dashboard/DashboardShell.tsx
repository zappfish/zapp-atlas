import { useEffect, type ReactNode } from "react";
import { useLocation } from "react-router";
import { DashMain, DashboardLayout } from "@/styles/elements";
import Sidebar from "./Sidebar";
import "@/styles/dashboard.css";

/**
 * Scrolls to the section a #hash names. Link changes the URL through the
 * History API, which does not scroll the way following an anchor does.
 */
const useHashScroll = () => {
  const { hash, pathname } = useLocation();

  useEffect(() => {
    if (!hash) return;
    // After paint: arriving from another group, the section is rendered in
    // this commit but not yet laid out. A section still loading is shorter
    // than it will be, so the scroll lands high and settles as rows arrive.
    const frame = requestAnimationFrame(() => {
      document
        .getElementById(hash.slice(1))
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    return () => cancelAnimationFrame(frame);
  }, [hash, pathname]);
};

/**
 * Layout for every signed-in page: the sidebar, and a panel the route fills.
 * Holds no data of its own — Sidebar fetches the group list, and whatever
 * renders as children fetches its own.
 */
const DashboardShell = ({ children }: { children: ReactNode }) => {
  useHashScroll();

  return (
    <DashboardLayout>
      <Sidebar />
      <DashMain>{children}</DashMain>
    </DashboardLayout>
  );
};

export default DashboardShell;
