import type { ReactNode } from "react";
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
  SubNav,
} from "./elements";
import type { Group } from "./placeholder";

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

const Sidebar = ({
  groups,
  activeId,
}: {
  groups: Group[];
  activeId: number;
}) => (
  <DashSidebar>
    <MySubmissionsLink href="/my-submissions">My Submissions</MySubmissionsLink>

    <SidebarHeading>My Research Groups</SidebarHeading>
    <GroupList>
      {groups.map((group) => (
        <GroupItem
          key={group.id}
          group={group}
          isActive={group.id === activeId}
        >
          <GroupSections groupId={group.id} />
        </GroupItem>
      ))}
    </GroupList>
  </DashSidebar>
);

export default Sidebar;
