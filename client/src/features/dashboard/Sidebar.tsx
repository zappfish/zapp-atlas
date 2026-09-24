import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useLocation } from "react-router";
import { fetchGroups } from "@/api/groups";
import { keys } from "@/api/hooks";
import AddGroupForm from "./AddGroupForm";
import {
  DashSidebar,
  GroupAvatar,
  GroupCaret,
  GroupList,
  GroupListItem,
  GroupName,
  GroupSummary,
  GroupSummaryBox,
  GroupText,
  MySubmissionsLink,
  SidebarHeading,
  SidebarToggle,
  SidebarTop,
  SkeletonText,
  SubNav,
} from "@/styles/elements";
import type { Group } from "@/api/groups";

/** The group list beside every dashboard page. */

/**
 * Two letters for the collapsed rail
 */
const initials = (name: string) => {
  const words = name.trim().split(/\s+/);
  const letters =
    words.length > 1
      ? words.slice(0, 2).map((word) => word[0] ?? "")
      : [...(words[0] ?? "").slice(0, 2)];
  return letters.join("").toUpperCase();
};

/** Either submission form: the bare one, or a group's. */
const onForm = (pathname: string) => pathname.endsWith("/submissions/new");

const GroupItem = ({
  group,
  isActive,
  isCollapsed,
  children,
}: {
  group: Group;
  isActive: boolean;
  isCollapsed: boolean;
  /** Sub-navigation, rendered only for the open group. */
  children?: ReactNode;
}) => (
  <GroupListItem>
    <GroupSummary
      isActive={isActive}
      to={`/research-groups/${group.id}`}
      title={isCollapsed ? group.name : undefined}
    >
      {isCollapsed ? (
        <GroupAvatar aria-hidden="true">{initials(group.name)}</GroupAvatar>
      ) : (
        <>
          <GroupText>
            <GroupName>{group.name}</GroupName>
          </GroupText>
          <GroupCaret aria-hidden="true">&rsaquo;</GroupCaret>
        </>
      )}
    </GroupSummary>
    {isActive && !isCollapsed && children}
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
  const [collapsed, setCollapsed] = useState(() => onForm(pathname));

  // Collapses on arriving at the form, where the group nav is not what the
  // page is for. Keyed on arrival rather than on the path, so expanding it
  // while there sticks.
  const wasOnForm = useRef(onForm(pathname));
  useEffect(() => {
    const isOnForm = onForm(pathname);
    if (isOnForm && !wasOnForm.current) setCollapsed(true);
    wasOnForm.current = isOnForm;
  }, [pathname]);

  const openForm = useCallback(() => setCreating(true), []);
  const closeForm = useCallback(() => setCreating(false), []);
  const toggle = useCallback(() => setCollapsed((was) => !was), []);

  return (
    <DashSidebar isCollapsed={collapsed}>
      <SidebarTop>
        <MySubmissionsLink
          to="/my-submissions"
          title={collapsed ? "My Submissions" : undefined}
        >
          {collapsed ? "MS" : "My Submissions"}
        </MySubmissionsLink>
        <SidebarToggle
          type="button"
          aria-expanded={!collapsed}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          onClick={toggle}
        >
          <span aria-hidden="true">{collapsed ? "›" : "‹"}</span>
        </SidebarToggle>
      </SidebarTop>

      {!collapsed && <SidebarHeading>My Research Groups</SidebarHeading>}
      {isPending ? (
        <SkeletonGroups />
      ) : (
        <GroupList>
          {(data ?? []).map((group) => (
            <GroupItem
              key={group.id}
              group={group}
              isActive={group.id === activeId}
              isCollapsed={collapsed}
            >
              <GroupSections groupId={group.id} />
            </GroupItem>
          ))}
        </GroupList>
      )}

      <button
        className="btn btn--secondary dash-new-group"
        type="button"
        title={collapsed ? "New group" : undefined}
        onClick={openForm}
      >
        {collapsed ? "+" : "+ New Group"}
      </button>

      <AddGroupForm open={creating} onClose={closeForm} />
    </DashSidebar>
  );
};

export default Sidebar;
