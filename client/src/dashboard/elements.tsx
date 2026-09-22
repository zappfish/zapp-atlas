import {
  createElement,
  type ComponentPropsWithoutRef,
  type ElementType,
} from "react";

/**
 * Every class name the dashboard uses, so no component renders a raw className.
 * Rules live in ./dashboard.css.
 *
 * `styled` fixes a tag and a class and spreads the rest, so elements still take
 * href, onClick and so on.
 */

const styled = <T extends ElementType>(tag: T, className: string) => {
  const Element = ({
    className: extra,
    ...rest
  }: ComponentPropsWithoutRef<T> & { className?: string }) =>
    createElement(tag, {
      // Appended, not replaced, so modifiers like "is-active" work.
      className: extra ? `${className} ${extra}` : className,
      ...rest,
    });
  Element.displayName = className;
  return Element;
};

const modifier = (on: boolean, name: string) => (on ? name : undefined);

/* ---- page ---- */

export const DashboardLayout = styled("div", "dashboard");
export const DashMain = styled("div", "dash-main");
export const DashHeader = styled("header", "dash-header");
export const DashEyebrow = styled("p", "dash-header__eyebrow");
export const DashTitle = styled("h1", "dash-header__title");

/* ---- sidebar ---- */

export const DashSidebar = styled("aside", "dash-sidebar");
export const MySubmissionsLink = styled("a", "dash-mysubs");
export const SidebarHeading = styled("h2", "dash-sidebar__heading");
export const GroupList = styled("ul", "dash-groups");
export const GroupListItem = styled("li", "dash-group");
export const GroupText = styled("span", "dash-group__text");
export const GroupName = styled("span", "dash-group__name");
export const GroupCaret = styled("span", "dash-group__caret");
export const SubNav = styled("ul", "dash-subnav");

const GroupSummaryLink = styled("a", "dash-group__summary");

export const GroupSummary = ({
  isActive,
  ...rest
}: ComponentPropsWithoutRef<"a"> & { isActive: boolean }) => (
  <GroupSummaryLink className={modifier(isActive, "is-active")} {...rest} />
);

/* ---- record sections ---- */

export const Section = styled("section", "dash-section");
export const SectionHead = styled("header", "dash-section__head");
export const SectionTitle = styled("h2", "dash-section__title");
export const Count = styled("span", "dash-count");
export const Rows = styled("div", "dash-rows");
export const Row = styled("div", "dash-row");
export const RowMain = styled("div", "dash-row__main");
export const RowLabel = styled("span", "dash-row__label");
export const RowSub = styled("span", "dash-row__sub");
export const MoreButton = styled("button", "dash-more");
export const SkeletonRow = styled("div", "dash-row dash-row--skeleton");

const SkeletonBar = styled("span", "dash-skeleton");

/** A grey bar standing in for text that has not arrived. */
export const SkeletonText = ({ width }: { width: string }) => (
  <SkeletonBar style={{ width }} aria-hidden="true" />
);

/* ---- empty states ---- */

export const Empty = styled("div", "dash-empty dash-empty--panel");
export const EmptyTitle = styled("p", "dash-empty__title");
export const EmptyText = styled("p", "dash-empty__text");

/* ---- submissions ---- */

export const SubmissionsSection = styled("section", "dash-submissions");
export const SubmissionsHead = styled("header", "dash-submissions__head");
export const SubmissionsTitle = styled("h2", "dash-card__title");
export const SubmissionTools = styled("div", "mysub-tools");
export const TabList = styled("div", "mysub-tabs");
export const TabCount = styled("span", "mysub-tab__n");
export const SubmissionList = styled("ul", "mysub-list");
export const SubmissionItem = styled("li", "mysub");
export const SubmissionInfo = styled("div", "mysub__info");
export const SubmissionTitle = styled("span", "mysub__title");
export const SubmissionMeta = styled("span", "mysub__meta");
export const StatusDot = styled("span", "mysub__dot");
export const SubmittedBy = styled("span", "mysub__by");
export const UpdatedOn = styled("span", "mysub__date");
export const MetaSeparator = styled("span", "mysub__sep");

const TabButton = styled("button", "mysub-tab");

export const Tab = ({
  isActive,
  ...rest
}: ComponentPropsWithoutRef<"button"> & { isActive: boolean }) => (
  <TabButton className={modifier(isActive, "is-active")} {...rest} />
);

const StatusBadge = styled("span", "mysub__status");

export const Status = ({
  status,
  ...rest
}: ComponentPropsWithoutRef<"span"> & { status: string }) => (
  // mysub__status--in-progress: the status picks the color.
  <StatusBadge
    className={`mysub__status--${status.toLowerCase().replace(/ /g, "-")}`}
    {...rest}
  />
);
