import { useGroupDashboard } from "@/api/hooks";
import Submissions from "@/features/submissions/Submissions";
import { MicroscopeIcon } from "@/components/icons";
import {
  DashEyebrow,
  DashHeader,
  DashTitle,
  GroupIdentity,
  GroupTile,
  SkeletonText,
} from "@/styles/elements";
import CabinetSection from "./CabinetSection";
import FishTankSection from "./FishTankSection";

/**
 * One research group. Each section owns its own records and the dialogs that
 * change them; submissions have no endpoint, so that list is empty.
 */
const GroupView = ({ groupId }: { groupId: number }) => {
  const { error, group, fishTank, cabinet } = useGroupDashboard(groupId);

  // A 404 is a group the caller is not in; the API does not distinguish that
  // from one that does not exist.
  if (error) {
    return <p>This research group is not available.</p>;
  }

  return (
    <>
      <DashHeader>
        <GroupIdentity>
          <GroupTile>
            <MicroscopeIcon />
          </GroupTile>
          <div>
            <DashEyebrow>Research group</DashEyebrow>
            <DashTitle>
              {group ? group.name : <SkeletonText width="12rem" />}
            </DashTitle>
          </div>
        </GroupIdentity>
      </DashHeader>

      <FishTankSection
        groupId={groupId}
        entries={fishTank.rows}
        isPending={fishTank.isPending}
      />

      <CabinetSection
        groupId={groupId}
        entries={cabinet.rows}
        isPending={cabinet.isPending}
      />

      <Submissions
        submissions={[]}
        emptyText="Create a submission to share this group's observations."
      />
    </>
  );
};

export default GroupView;
