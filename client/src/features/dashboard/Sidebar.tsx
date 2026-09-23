import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useLocation } from "react-router";
import { fetchGroups } from "@/api/groups";
import { keys } from "@/api/hooks";
import AddGroupForm from "./AddGroupForm";
import {
  DashSidebar,
  GroupCaret,
  GroupList,
  GroupListItem,
  GroupName,
  GroupSummary,
  GroupSummaryBox,
  GroupText,
  MySubmissionsLink,
  SidebarHeading,
  SkeletonText,
  SubNav,
} from "@/styles/elements";
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
    <GroupSummary isActive={isActive} to={`/research-groups/${group.id}`}>
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

const GroupSections = ({ groupId }: { groupId: number }) => {
  // The section being read, from the hash the sidebar's own links set.
  const { hash } = useLocation();
  const active = hash.slice(1);

  return (
    <SubNav>
      {SECTIONS.map(({ slug, label }) => (
        <li key={slug}>
          <Link
            to={`/research-groups/${groupId}#${slug}`}
            className={slug === active ? "is-active" : undefined}
          >
            {label}
          </Link>
        </li>
      ))}
    </SubNav>
  );
};

const SkeletonGroups = () => (
  <GroupList aria-hidden="true">
    {Array.from({ length: 3 }, (_, i) => (
      <GroupListItem key={i}>
        <GroupSummaryBox>
          <GroupText>
            <SkeletonText width="8rem" />
          </GroupText>
        </GroupSummaryBox>
      </GroupListItem>
    ))}
  </GroupList>
);

const Sidebar = () => {
  const { isPending, data } = useQuery({
    queryKey: keys.groups,
    queryFn: ({ signal }) => fetchGroups(signal),
  });
  // Outside <Routes>, so it reads the location rather than route params: it
  // has to mark the open group from any page.
  const { pathname } = useLocation();
  const match = pathname.match(/^\/research-groups\/(\d+)/);
  const activeId = match ? Number(match[1]) : null;
  const [creating, setCreating] = useState(false);

  return (
    <DashSidebar>
      <MySubmissionsLink to="/my-submissions">
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

      <button
        className="btn btn--secondary dash-new-group"
        type="button"
        onClick={() => setCreating(true)}
      >
        + New Group
      </button>

      <AddGroupForm open={creating} onClose={() => setCreating(false)} />
    </DashSidebar>
  );
};

export default Sidebar;
