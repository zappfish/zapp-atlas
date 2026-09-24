import { useCallback, useState } from "react";
import { Link } from "react-router";
import { useGroupDashboard } from "@/api/hooks";
import {
  CrumbSeparator,
  Crumbs,
  FormIntro,
  FormIntroText,
  FormLayout,
  FormMain,
  RequiredMark,
  TextInput,
} from "@/styles/elements";
import Field from "./Field";
import FormActions from "./FormActions";
import FormNav from "./FormNav";
import FormSection from "./FormSection";
import ImagesSection from "./sections/ImagesSection";
import { SECTIONS, type SectionSlug, type SectionStatus } from "./sections";
import "./form.css";

/**
 * A specimen submission.
 *
 * Layout only: the sections are empty until their fields are built, and the
 * statuses are placeholders — each will be derived from its own fields.
 */

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

/** Placeholders until each section can be measured against its own fields. */
const PLACEHOLDER_STATUS: Record<SectionSlug, SectionStatus> = {
  images: "in-progress",
  provenance: "not-started",
  fish: "not-started",
  experiment: "not-started",
  control: "not-started",
  phenotype: "not-started",
};

const SubmissionForm = ({ groupId }: { groupId?: number }) => {
  const [active, setActive] = useState<SectionSlug>("images");

  const jumpTo = useCallback((slug: SectionSlug) => {
    setActive(slug);
    document.getElementById(slug)?.scrollIntoView({ behavior: "smooth" });
  }, []);

  return (
    <FormLayout>
      <FormNav
          statuses={PLACEHOLDER_STATUS}
          active={active}
          onJump={jumpTo}
        />

      <FormMain>
        {groupId !== undefined && <GroupCrumbs groupId={groupId} />}
        <FormIntro>
          <Field
            label="Submission title"
            required
            hint="Give your submission a short, descriptive name."
          >
            {(id) => (
              <TextInput
                id={id}
                placeholder="e.g. Zebrafish cardiac development study"
              />
            )}
          </Field>

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
            isActive={slug === active}
          >
            {slug === "images" && <ImagesSection />}
          </FormSection>
        ))}

        <FormActions />
      </FormMain>
    </FormLayout>
  );
};

export default SubmissionForm;
