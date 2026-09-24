import {
  createElement,
  type ComponentPropsWithoutRef,
  type ElementType,
} from "react";
import { Link } from "react-router";

/**
 * Every class name the dashboard uses, so no component renders a raw className.
 * Rules live in ./dashboard.css.
 *
 * `styled` fixes a tag and a class and spreads the rest, so elements still take
 * href, onClick and so on. The tag can be a component: navigation elements are
 * built on Link, which swaps the view without reloading the page.
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
export const GroupIdentity = styled("div", "dash-identity");
export const GroupTile = styled("span", "dash-identity__tile");

/* ---- sidebar ---- */

export const DashSidebar = styled("aside", "dash-sidebar");
export const MySubmissionsLink = styled(Link, "dash-mysubs");
export const SidebarHeading = styled("h2", "dash-sidebar__heading");
export const GroupList = styled("ul", "dash-groups");
export const GroupListItem = styled("li", "dash-group");
export const GroupText = styled("span", "dash-group__text");
export const GroupName = styled("span", "dash-group__name");
export const GroupCaret = styled("span", "dash-group__caret");
export const SubNav = styled("ul", "dash-subnav");

const GroupSummaryLink = styled(Link, "dash-group__summary");

export const GroupSummary = ({
  isActive,
  ...rest
}: ComponentPropsWithoutRef<typeof Link> & { isActive: boolean }) => (
  <GroupSummaryLink className={modifier(isActive, "is-active")} {...rest} />
);

/** The same row with nowhere to go, for the loading state. */
export const GroupSummaryBox = styled("div", "dash-group__summary");

/* ---- record detail pages ---- */

export const Crumbs = styled("nav", "crumbs");
export const CrumbSeparator = styled("span", "crumbs__sep");
export const DetailSummary = styled("section", "detail-summary");
export const DetailList = styled("dl", "detail-list");
export const DetailHead = styled("div", "detail-list__head");
export const DetailItem = styled("div", "detail-item");
export const DetailLabel = styled("dt", "detail-item__label");
export const DetailValue = styled("dd", "detail-item__value");

/* ---- record sections ---- */

export const Section = styled("section", "dash-section");
export const SectionHead = styled("header", "dash-section__head");
export const SectionTitle = styled("h2", "dash-section__title");
export const SectionTools = styled("div", "dash-section__tools");
export const Count = styled("span", "dash-count");
export const Rows = styled("div", "dash-rows");
export const Row = styled("div", "dash-row");
export const RowMain = styled("div", "dash-row__main");
export const RowLabel = styled("span", "dash-row__label");
export const RowSub = styled("span", "dash-row__sub");
export const RowActions = styled("div", "dash-row__actions");
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

/* ---- submission form ---- */

export const FormLayout = styled("div", "form-layout");
export const FormMain = styled("div", "form-main");
export const FormIntro = styled("header", "form-intro");
export const FormIntroTitle = styled("h1", "form-intro__title");
export const FormIntroText = styled("p", "form-intro__text");
export const RequiredMark = styled("span", "form-required");

export const Nav = styled("aside", "form-nav");
export const NavHeading = styled("h2", "form-nav__heading");
export const NavList = styled("ol", "form-nav__list");
export const NavNumber = styled("span", "form-nav__number");
export const NavLabel = styled("span", "form-nav__label");
export const NavLegend = styled("ul", "form-nav__legend");

const NavItemButton = styled("button", "form-nav__item");

export const NavButton = ({
  isActive,
  ...rest
}: ComponentPropsWithoutRef<"button"> & { isActive: boolean }) => (
  <NavItemButton className={modifier(isActive, "is-active")} {...rest} />
);

export const FormSectionBox = styled("section", "form-section");
export const FormSectionHead = styled("header", "form-section__head");
export const FormSectionNumber = styled("span", "form-section__number");
export const FormSectionHeading = styled("div", "form-section__heading");
export const FormSectionTitle = styled("h2", "form-section__title");
export const FormSectionDescription = styled("p", "form-section__description");
export const FormSectionToggle = styled("button", "form-section__toggle");
export const FormSectionBody = styled("div", "form-section__body");
export const VisuallyHidden = styled("span", "visually-hidden");
