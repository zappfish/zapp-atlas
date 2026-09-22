import { useGroupDashboard } from "@/api/queries";
import type { CabinetEntry, FishTankEntry } from "@/api/groups";
import {
  DashEyebrow,
  DashHeader,
  DashMain,
  DashTitle,
  DashboardLayout,
  SkeletonText,
} from "./elements";
import RecordSection, { type Row } from "./RecordSection";
import Sidebar from "./Sidebar";
import Submissions from "./Submissions";
import "./dashboard.css";

/**
 * A research group's dashboard. The add, edit and remove actions are not
 * wired yet, and submissions have no endpoint, so that list is empty.
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

/** The page frame with every part still loading. */
export const DashboardSkeleton = () => (
  <DashboardLayout>
    <Sidebar groups={[]} activeId={0} isPending />
    <DashMain>
      <DashHeader>
        <div>
          <DashEyebrow>Research group</DashEyebrow>
          <DashTitle>
            <SkeletonText width="12rem" />
          </DashTitle>
        </div>
      </DashHeader>
      <RecordSection id="fish-tank" title="Fish Tank" rows={[]} isPending />
      <RecordSection
        id="chemical-cabinet"
        title="Chemical Cabinet"
        rows={[]}
        isPending
      />
    </DashMain>
  </DashboardLayout>
);

const Dashboard = ({ groupId }: { groupId: number }) => {
  const { error, groups, group, fishTank, cabinet } =
    useGroupDashboard(groupId);
  // A 404 is a group the caller is not in; the API does not distinguish that
  // from one that does not exist.
  if (error) {
    return <DashboardLayout>This research group is not available.</DashboardLayout>;
  }

  return (
    <DashboardLayout>
      <Sidebar
        groups={groups.rows}
        activeId={groupId}
        isPending={groups.isPending}
      />

      <DashMain>
        <DashHeader>
          <div>
            <DashEyebrow>Research group</DashEyebrow>
            <DashTitle>
              {group ? group.name : <SkeletonText width="12rem" />}
            </DashTitle>
          </div>
        </DashHeader>

        <RecordSection
          id="fish-tank"
          title="Fish Tank"
          rows={fishRows(fishTank.rows)}
          isPending={fishTank.isPending}
          emptyText="Add a fish line to start building this group's tank."
        />

        <RecordSection
          id="chemical-cabinet"
          title="Chemical Cabinet"
          rows={cabinetRows(cabinet.rows)}
          isPending={cabinet.isPending}
          emptyText="Add a chemical to this group's cabinet."
        />

        <Submissions submissions={[]} />
      </DashMain>
    </DashboardLayout>
  );
};

export default Dashboard;
