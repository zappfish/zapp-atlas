import {
  DashEyebrow,
  DashHeader,
  DashMain,
  DashTitle,
  DashboardLayout,
} from "./elements";
import RecordSection, { type Row } from "./RecordSection";
import Sidebar from "./Sidebar";
import Submissions from "./Submissions";
import { PLACEHOLDER, type CabinetEntry, type FishTankEntry } from "./placeholder";
import "./dashboard.css";

/**
 * A research group's dashboard. Placeholder data for now — the /api reads and
 * the add/edit/remove actions are not wired yet.
 */

const fishRows = (entries: FishTankEntry[]): Row[] =>
  entries.map((entry) => ({
    id: entry.id,
    label: entry.fish.name,
    sublabel: entry.fish.zfin_id,
  }));

// Only a chemical id for now; a name would become the label and this the sub.
const cabinetRows = (entries: CabinetEntry[]): Row[] =>
  entries.map((entry) => ({ id: entry.id, label: entry.chemical_id }));

const Dashboard = () => {
  const { groups, group, fishTank, cabinet, submissions } = PLACEHOLDER;

  return (
    <DashboardLayout>
      <Sidebar groups={groups} activeId={group.id} />

      <DashMain>
        <DashHeader>
          <div>
            <DashEyebrow>Research group</DashEyebrow>
            <DashTitle>{group.name}</DashTitle>
          </div>
        </DashHeader>

        <RecordSection
          id="fish-tank"
          title="Fish Tank"
          rows={fishRows(fishTank)}
          emptyText="Add a fish line to start building this group's tank."
        />

        <RecordSection
          id="chemical-cabinet"
          title="Chemical Cabinet"
          rows={cabinetRows(cabinet)}
          emptyText="Add a chemical to this group's cabinet."
        />

        <Submissions submissions={submissions} />
      </DashMain>
    </DashboardLayout>
  );
};

export default Dashboard;
