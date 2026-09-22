import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchGroups } from "@/api/groups";
import { keys } from "@/api/queries";
import {
  DashSidebar,
  GroupCaret,
  GroupList,
  GroupListItem,
  GroupName,
  GroupSummary,
  GroupText,
  MySubmissionsLink,
  SidebarHeading,
  SkeletonText,
  SubNav,
} from "./elements";
import type { Group } from "@/api/groups";

/** The group list beside every dashboard page. */

const GroupItem = ({
  group,
  isActive,
  children,
}: {
  group: Group;
  isActive: boolean;
  /** Sub-navigation, rendered only for the open group. */
  children?: ReactNode;
}) => (
  <GroupListItem>
    <GroupSummary isActive={isActive} href={`/research-groups/${group.id}`}>
      <GroupText>
        <GroupName>{group.name}</GroupName>
      </GroupText>
      <GroupCaret aria-hidden="true">&rsaquo;</GroupCaret>
    </GroupSummary>
    {isActive && children}
  </GroupListItem>
);

const SECTIONS = [
  { slug: "fish-tank", label: "Fish Tank" },
  { slug: "chemical-cabinet", label: "Chemical Cabinet" },
  { slug: "submissions", label: "Submissions" },
];

const GroupSections = ({ groupId }: { groupId: number }) => (
  <SubNav>
    {SECTIONS.map(({ slug, label }) => (
      <li key={slug}>
        <a href={`/research-groups/${groupId}#${slug}`}>{label}</a>
      </li>
    ))}
  </SubNav>
);

const SkeletonGroups = () => (
  <GroupList aria-hidden="true">
    {Array.from({ length: 3 }, (_, i) => (
      <GroupListItem key={i}>
        <GroupSummary isActive={false}>
          <GroupText>
            <SkeletonText width="8rem" />
          </GroupText>
        </GroupSummary>
      </GroupListItem>
    ))}
  </GroupList>
);

/** The open group, from /research-groups/{id}. Null on any other page. */
const activeGroupId = (): number | null => {
  const match = window.location.pathname.match(/^\/research-groups\/(\d+)/);
  return match ? Number(match[1]) : null;
};

const Sidebar = () => {
  const { isPending, data } = useQuery({
    queryKey: keys.groups,
    queryFn: ({ signal }) => fetchGroups(signal),
  });
  const activeId = activeGroupId();

  return (
    <DashSidebar>
      <MySubmissionsLink href="/my-submissions">
        My Submissions
      </MySubmissionsLink>

      <SidebarHeading>My Research Groups</SidebarHeading>
      {isPending ? (
        <SkeletonGroups />
      ) : (
        <GroupList>
          {(data ?? []).map((group) => (
            <GroupItem
              key={group.id}
              group={group}
              isActive={group.id === activeId}
            >
              <GroupSections groupId={group.id} />
            </GroupItem>
          ))}
        </GroupList>
      )}
    </DashSidebar>
  );
};

export default Sidebar;
