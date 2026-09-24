import { useCallback, useState } from "react";
import { Link } from "react-router";
import { useGroupDashboard } from "@/api/hooks";
import {
  CrumbSeparator,
  Crumbs,
  FormIntro,
  FormIntroText,
  FormIntroTitle,
  FormLayout,
  FormMain,
  RequiredMark,
} from "@/styles/elements";
import FormNav from "./FormNav";
import FormSection from "./FormSection";
import { SECTIONS, type SectionSlug, type SectionStatus } from "./sections";
import "./form.css";

/**
 * A specimen submission.
 *
 * Layout only: the sections are empty until their fields are built, and the
 * statuses are placeholders — each will be derived from its own fields.
 */

const DESCRIPTIONS: Record<SectionSlug, string> = {
  images:
    "Upload and describe all images associated with this specimen submission. Each image entry requires a file, type, and anatomical view. Acquisition metadata applies to all images in this submission unless overridden per image.",
  provenance:
    "Who produced this data and where it was published, so an entry can be traced back to its source.",
  fish: "The fish this submission describes — chosen from your group's tank, or described here.",
  experiment:
    "The substance the fish was exposed to, and how that exposure was carried out.",
  control: "The untreated or vehicle-treated fish this observation is measured against.",
  phenotype:
    "What was observed, at what stage, and how prevalent and severe it was.",
};

const PLACEHOLDER_STATUS: Record<SectionSlug, SectionStatus> = {
  images: "in-progress",
  provenance: "not-started",
  fish: "not-started",
  experiment: "not-started",
  control: "not-started",
  phenotype: "not-started",
};

/** Where the form was started from, when it was started from a group. */
const GroupCrumbs = ({ groupId }: { groupId: number }) => {
  const { group } = useGroupDashboard(groupId);

  return (
    <Crumbs aria-label="Breadcrumb">
      <Link to={`/research-groups/${groupId}`}>{group?.name ?? "Group"}</Link>
      <CrumbSeparator aria-hidden="true">›</CrumbSeparator>
      <span aria-current="page">New submission</span>
    </Crumbs>
  );
};

const SubmissionForm = ({ groupId }: { groupId?: number }) => {
  const [active, setActive] = useState<SectionSlug>("images");

  const jumpTo = useCallback((slug: SectionSlug) => {
    setActive(slug);
    document.getElementById(slug)?.scrollIntoView({ behavior: "smooth" });
  }, []);

  return (
    <FormLayout>
      <FormNav statuses={PLACEHOLDER_STATUS} active={active} onJump={jumpTo} />

      <FormMain>
        {groupId !== undefined && <GroupCrumbs groupId={groupId} />}
        <FormIntro>
          <FormIntroTitle>New Submission</FormIntroTitle>
          <FormIntroText>
            Complete all required fields marked with{" "}
            <RequiredMark>*</RequiredMark> before submitting. You may save a
            draft at any time and return later. Collapse sections you have
            completed to keep the form manageable.
          </FormIntroText>
        </FormIntro>

        {SECTIONS.map(({ slug, label }) => (
          <FormSection
            key={slug}
            slug={slug}
            title={label}
            description={DESCRIPTIONS[slug]}
            isActive={slug === active}
          />
        ))}
      </FormMain>
    </FormLayout>
  );
};

export default SubmissionForm;
