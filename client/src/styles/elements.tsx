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

const SidebarPanel = styled("aside", "dash-sidebar");

export const DashSidebar = ({
  isCollapsed,
  ...rest
}: ComponentPropsWithoutRef<"aside"> & { isCollapsed: boolean }) => (
  <SidebarPanel
    className={modifier(isCollapsed, "dash-sidebar--collapsed")}
    {...rest}
  />
);

export const SidebarTop = styled("div", "dash-sidebar__top");
export const SidebarToggle = styled("button", "dash-sidebar__toggle");
export const MySubmissionsLink = styled(Link, "dash-mysubs");
export const SidebarHeading = styled("h2", "dash-sidebar__heading");
export const GroupList = styled("ul", "dash-groups");
export const GroupListItem = styled("li", "dash-group");
export const GroupText = styled("span", "dash-group__text");
export const GroupName = styled("span", "dash-group__name");
export const GroupCaret = styled("span", "dash-group__caret");
export const GroupAvatar = styled("span", "dash-group__avatar");
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
export const FormMain = styled("form", "form-main");
/** What the form collected, until there is somewhere to send it. */
export const CollectedValues = styled("pre", "form-collected");
export const FormIntro = styled("header", "form-intro");
export const RequiredMark = styled("span", "form-required");

export const Nav = styled("aside", "form-nav");
export const NavProgress = styled("div", "form-progressbar");
export const NavProgressHead = styled("p", "form-progressbar__head");
export const NavProgressCount = styled("span", "form-progressbar__count");
export const NavProgressPercent = styled("span", "form-progressbar__percent");
export const NavProgressTrack = styled("div", "form-progressbar__track");
export const NavProgressFill = styled("div", "form-progressbar__fill");
export const NavStep = styled("span", "form-nav__step");

export const PageTitle = styled("h1", "form-page__title");
export const PageLead = styled("p", "form-page__lead");
export const PageHead = styled("header", "form-page__head");
export const SectionEyebrow = styled("p", "form-section__eyebrow");
export const AnnotatorPanel = styled("div", "annotator");
export const ProgressBanner = styled("p", "form-banner");
export const ActionsPrompt = styled("div", "form-actions__prompt");
export const ActionsTitle = styled("p", "form-actions__title");
export const ActionsHint = styled("p", "form-actions__hint");
export const BannerStrong = styled("span", "form-banner__title");
export const NavHeading = styled("h2", "form-nav__heading");
export const NavList = styled("ol", "form-nav__list");
export const NavLabel = styled("span", "form-nav__label");

const NavItemButton = styled("button", "form-nav__item");

export const NavButton = ({
  isActive,
  ...rest
}: ComponentPropsWithoutRef<"button"> & { isActive: boolean }) => (
  <NavItemButton className={modifier(isActive, "is-active")} {...rest} />
);

const FormSectionFrame = styled("section", "form-section");

export const FormSectionBox = ({
  isOpen,
  isActive,
  ...rest
}: ComponentPropsWithoutRef<"section"> & {
  isOpen: boolean;
  isActive: boolean;
}) => (
  <FormSectionFrame
    className={
      [
        isOpen ? null : "form-section--collapsed",
        isActive ? "form-section--active" : null,
      ]
        .filter(Boolean)
        .join(" ") || undefined
    }
    {...rest}
  />
);
export const FormSectionHead = styled("header", "form-section__head");
export const FormSectionHeading = styled("div", "form-section__heading");
export const FormSectionTitle = styled("h2", "form-section__title");
export const FormSectionToggle = styled("button", "form-section__toggle");
export const FormSectionBody = styled("div", "form-section__body");
export const FormActionBar = styled("div", "form-actions");
export const VisuallyHidden = styled("span", "visually-hidden");


/* ---- form fields ---- */

export const FieldBox = styled("div", "field");
export const FieldLabel = styled("label", "field__label");
export const FieldHint = styled("p", "field__hint");
export const FieldError = styled("p", "field__error");
/** Sibling row: a <label> cannot contain a <button>. */
export const FieldLabelRow = styled("div", "field__label-row");
export const InfoTipBox = styled("span", "infotip");
export const InfoTipButton = styled("button", "infotip__button");
export const InfoTipBubble = styled("div", "infotip__bubble");
export const TextInput = styled("input", "field__input");
/** A value the form shows but does not collect. Text, not a box. */
export const FieldValue = styled("p", "field__value");
/** Its label: a span, since `<label for>` binds only to form controls. */
export const FieldValueLabel = styled("span", "field__label");
export const TextArea = styled("textarea", "field__input field__input--area");
export const SelectInput = styled("select", "field__input");
/** A unit beside its value in a MeasureRow. */
export const ShortSelect = styled("select", "field__input field__input--short");
export const FieldGrid = styled("div", "field-grid");
/** A row of numbers and their units, which sit three to a row. */
export const MeasureGrid = styled("div", "field-grid--measures");
/** A field grid held to two columns, for a section with a tall field in it. */
export const FieldNote = styled("p", "field__note");


export const EntryCard = styled("div", "form-entry");
/** Names one of several repeated entries, and removes it. */
export const EntryHead = styled("div", "form-entry__head");
export const EntryTitle = styled("h3", "form-entry__title");
export const EntryRemove = styled("button", "form-entry__remove");
/** Folds one group of a repeating section away. */
export const GroupToggle = styled("button", "form-entry__toggle");
const EntryCaretGlyph = styled("span", "form-entry__caret");

/** Points at the title when folded, and down when open. */
export const EntryCaret = ({
  isOpen,
  ...rest
}: ComponentPropsWithoutRef<"span"> & { isOpen: boolean }) => (
  <EntryCaretGlyph className={modifier(isOpen, "is-open")} {...rest} />
);
/** What a folded group holds, so it can be told from its neighbours. */
export const GroupSummaryText = styled("p", "form-entry__summary");
export const EntryBody = styled("div", "image-entry");
export const EntryMeta = styled("div", "image-entry__meta");
export const EntryFooter = styled("div", "form-entry__footer");
export const AddRow = styled("div", "form-add");
/** An add button that belongs to the group above it, not to the section. */
export const AddRowInline = styled("div", "form-add form-add--inline");
export const AddButton = styled("button", "form-add__button");

export const Upload = styled("div", "upload");
const UploadPaneBox = styled("div", "upload__pane");

export const UploadPane = ({
  isDragging,
  ...rest
}: ComponentPropsWithoutRef<"div"> & { isDragging: boolean }) => (
  <UploadPaneBox className={modifier(isDragging, "is-dragging")} {...rest} />
);
export const UploadChosen = styled("div", "upload__chosen");
export const PreviewImage = styled("img", "upload__image");
/** Fallback for a file <img> cannot render. */
export const UploadFile = styled("div", "upload__file");
export const UploadFileName = styled("p", "upload__file-name");
export const UploadHint = styled("p", "upload__hint");
export const UploadLimits = styled("p", "upload__limits");
export const PreviewActions = styled("div", "upload__preview-actions");
export const PreviewAction = styled("button", "upload__action");
export const PreviewRemove = styled("button", "upload__action upload__action--remove");

export const MeasureRow = styled("div", "measure-row");
export const MeasureInput = styled("div", "field__suffix-box");
export const MeasureSuffix = styled("span", "field__suffix");
/** A field that takes the whole row: radios, or a box that follows them. */

export const RadioGroup = styled("div", "radio-group");
export const RadioLabel = styled("label", "radio-group__option");
/** Keeps the InfoTip outside the <label>, so clicking it does not select. */
export const RadioItem = styled("span", "radio-group__item");
export const NotesToggle = styled("button", "notes-toggle");
export const Notes = styled("div", "notes");
export const NotesRemove = styled("button", "notes__remove");

/* ---- dialogs ---- */

export const ModalPanel = styled("div", "modal__panel");
export const ModalForm = styled("form", "modal__panel");
/* Heading and actions stay put; the middle scrolls. */
export const ModalBanded = styled("div", "modal__panel modal__panel--flush");
export const ModalHead = styled("header", "modal__head");
export const ModalBody = styled("div", "modal__body");
export const ModalFoot = styled("footer", "modal__foot");
export const ModalTitle = styled("h2", "modal__title");
export const ModalText = styled("p", "modal__text");
export const ModalField = styled("label", "modal__field");
export const ModalLabel = styled("span", "modal__label");
export const ModalInput = styled("input", "modal__input");
export const ModalSelect = styled("select", "modal__input");
export const ModalActions = styled("div", "modal__actions");

/* ---- searching a reference database ---- */

export const TermSearch = styled("div", "termsearch");
export const SearchFields = styled("div", "termsearch__fields");
export const SearchType = styled("label", "termsearch__type");
export const SearchQuery = styled("label", "termsearch__query");
export const SearchBox = styled("span", "termsearch__box");
export const SearchIconSlot = styled("span", "termsearch__search-icon");
export const SearchInput = styled("input", "termsearch__input");
export const SearchClear = styled("button", "termsearch__clear");
export const SearchList = styled("ul", "termsearch__list");
export const SearchOption = styled("button", "termsearch__option");
export const OptionText = styled("span", "termsearch__option-text");
export const OptionName = styled("span", "termsearch__option-name");
export const OptionId = styled("span", "termsearch__option-id");
export const OptionNote = styled("span", "termsearch__option-note");
export const SearchHint = styled("p", "termsearch__hint");
/** Said when a search ran and matched nothing, in place of the hint. */
export const SearchMiss = styled("p", "termsearch__miss");
export const StageButton = styled("button", "btn btn--primary termsearch__stage");
/* The hint and the button share a line: the button is what the hint asks for. */
export const SearchFooter = styled("div", "termsearch__footer");

export const Preview = styled("div", "termsearch__preview");
export const PreviewIcon = styled("span", "termsearch__preview-icon");
export const PreviewName = styled("p", "termsearch__preview-name");
export const PreviewId = styled("p", "termsearch__preview-id");
export const PreviewDescription = styled("p", "termsearch__preview-description");

/* ---- staged in a dialog ---- */

export const Staged = styled("section", "staged");
export const StagedHead = styled("header", "staged__head");
export const StagedTitle = styled("h3", "staged__title");
export const StagedCount = styled("span", "staged__count");
export const StagedLead = styled("p", "staged__lead");
export const StagedEmpty = styled("div", "staged__empty");
export const StagedEmptyIcon = styled("span", "staged__empty-icon");
export const StagedEmptyCopy = styled("div", "staged__empty-copy");
export const StagedEmptyTitle = styled("p", "staged__empty-title");
export const StagedEmptyText = styled("p", "staged__empty-text");
export const StagedList = styled("ul", "staged__list");
export const StagedItem = styled("li", "staged__item");
export const StagedNumber = styled("span", "staged__number");
export const StagedNames = styled("div", "staged__names");
export const StagedName = styled("p", "staged__name");
export const StagedId = styled("p", "staged__id");
export const StagedError = styled("p", "staged__error");
export const StagedNickname = styled("input", "staged__nickname");
export const StagedRemove = styled("button", "staged__remove");


/* ---- a row's actions ---- */

export const RowMenuToggle = styled("summary", "dash-icon-btn sub-menu__toggle");
export const RowMenuList = styled("div", "panel sub-menu__list");

/** `isDanger` marks the destructive one. */
export const RowMenuAction = ({
  isDanger,
  ...rest
}: ComponentPropsWithoutRef<"button"> & { isDanger: boolean }) => (
  <MenuItem className={modifier(isDanger, "sub-menu__item--danger")} {...rest} />
);

const MenuItem = styled("button", "sub-menu__item");

/* ---- choosing an exposure's chemical ---- */

export const SubstanceCard = styled("div", "substance");
export const SubstanceChosen = styled("div", "substance__chosen");
export const SubstanceIcon = styled("span", "substance__icon");
export const SubstanceNames = styled("div", "substance__names");
export const SubstanceName = styled("p", "substance__name");
export const SubstanceId = styled("p", "substance__id");
export const SubstanceAdd = styled("button", "substance__add");
export const SubstanceSaved = styled("span", "substance__saved");
export const SubstanceChange = styled("button", "substance__change");
export const SubstanceHead = styled("header", "substance__head");
export const SubstanceBody = styled("div", "substance__body");
export const SubstanceTitle = styled("h4", "substance__title");
export const SubstanceLead = styled("p", "substance__lead");
export const SubstanceBack = styled("button", "substance__back");
export const SubstanceChoices = styled("div", "substance__choices");
export const SubstanceOr = styled("span", "substance__or");
export const SubstanceSearch = styled("button", "substance__search");

/* ---- a group's members ---- */

export const MembersButton = styled("button", "members-button");
export const MembersCount = styled("span", "members-button__count");
export const MembersSubhead = styled("h3", "members__subhead");
export const MembersDivider = styled("hr", "members__divider");
export const MembersList = styled("ul", "member-list");
export const MembersAdd = styled("form", "member-add");
export const MemberRow = styled("li", "member");
export const MemberAvatar = styled("span", "member__avatar");
export const MemberWho = styled("span", "member__who");
export const MemberName = styled("span", "member__name");
export const MemberOrcid = styled("span", "member__orcid");

/** Admin and member read differently, so the role is not just a word. */
export const MemberRole = ({
  isAdmin,
  ...rest
}: ComponentPropsWithoutRef<"span"> & { isAdmin: boolean }) => (
  <RoleTag className={isAdmin ? "member__role--admin" : "member__role--member"} {...rest} />
);

const RoleTag = styled("span", "member__role");
