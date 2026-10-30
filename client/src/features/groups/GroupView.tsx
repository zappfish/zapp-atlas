import { useState } from "react";
import { useGroupDashboard } from "@/api/hooks";
import Submissions from "@/features/submissions/Submissions";
import { MicroscopeIcon, UsersIcon } from "@/components/icons";
import {
  DashEyebrow,
  DashHeader,
  DashTitle,
  GroupIdentity,
  GroupTile,
  MembersButton,
  MembersCount,
  SkeletonText,
} from "@/styles/elements";
import CabinetSection from "./CabinetSection";
import MembersForm from "./MembersForm";
import FishTankSection from "./FishTankSection";
import StudiesSection from "./StudiesSection";

/**
 * One research group. Each section owns its own records and the dialogs that
 * change them; submissions have no endpoint, so that list is empty.
 */
const GroupView = ({ groupId }: { groupId: number }) => {
  const { error, group, members, fishTank, cabinet } = useGroupDashboard(groupId);
  const [isMembersOpen, setIsMembersOpen] = useState(false);

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

        <MembersButton type="button" onClick={() => setIsMembersOpen(true)}>
          <UsersIcon />
          Members
          <MembersCount>{members.length}</MembersCount>
        </MembersButton>
      </DashHeader>

      <MembersForm
        groupId={groupId}
        open={isMembersOpen}
        onClose={() => setIsMembersOpen(false)}
      />

      <FishTankSection
        groupId={groupId}
        entries={fishTank.rows}
        isPending={fishTank.isPending}
        error={fishTank.error}
        onRetry={fishTank.retry}
      />

      <CabinetSection
        groupId={groupId}
        entries={cabinet.rows}
        isPending={cabinet.isPending}
        error={cabinet.error}
        onRetry={cabinet.retry}
      />

      <StudiesSection groupId={groupId} />

      <Submissions
        submissions={[]}
        emptyText="Create a submission to share this group's observations."
        newHref={`/research-groups/${groupId}/submissions/new`}
      />
    </>
  );
};

export default GroupView;
