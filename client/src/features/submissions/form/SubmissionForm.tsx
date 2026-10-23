import { useCallback, useState, type ReactNode } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { Link } from "react-router";
import { useGroupDashboard } from "@/api/hooks";
import {
  CrumbSeparator,
  Crumbs,
  FormIntro,
  FormLayout,
  BannerStrong,
  CollectedValues,
  FormMain,
  PageHead,
  PageLead,
  PageTitle,
  ProgressBanner,
  TextInput,
} from "@/styles/elements";
import Field from "./Field";
import { emptySubmission, type Submission } from "./submission";
import { sectionStatus } from "./status";
import FormActions from "./FormActions";
import FormNav from "./FormNav";
import FormSection from "./FormSection";
import ControlSection from "./sections/ControlSection";
import ExperimentSection from "./sections/ExperimentSection";
import FishSection from "./sections/FishSection";
import ImagesSection from "./sections/ImagesSection";
import PhenotypeSection from "./sections/PhenotypeSection";
import ProvenanceSection from "./sections/ProvenanceSection";
import { SECTIONS, type SectionSlug, type SectionStatus } from "./sections";
import "./form.css";

/** What a section looks like before anyone has touched it. */
const UNTOUCHED = emptySubmission();

/** `groupId` reaches the exposure's chemical picker, which offers that
 *  group's cabinet alongside the database search. */
const SECTION_BODIES: Record<SectionSlug, (groupId: number) => ReactNode> = {
  provenance: () => <ProvenanceSection />,
  images: () => <ImagesSection />,
  fish: () => <FishSection />,
  experiment: (groupId) => <ExperimentSection groupId={groupId} />,
  control: () => <ControlSection />,
  phenotype: () => <PhenotypeSection />,
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

const SubmissionForm = ({ groupId }: { groupId: number }) => {
  // The first section, whatever the order in sections.ts says it is.
  const [active, setActive] = useState<SectionSlug>(SECTIONS[0].slug);
  const [collected, setCollected] = useState<Submission | null>(null);
  const form = useForm<Submission>({
    defaultValues: emptySubmission(),
    // Checked on leaving a field, then as it is corrected.
    mode: "onTouched",
  });

  // Watched, so a dot answers to what has been typed rather than to a save.
  const values = form.watch();
  const statuses = Object.fromEntries(
    SECTIONS.map(({ slug }) => [slug, sectionStatus(slug, values, UNTOUCHED)]),
  ) as Record<SectionSlug, SectionStatus>;

  // Read off those statuses, so the summary and the dots cannot disagree.
  const complete = Object.values(statuses).filter(
    (status) => status === "complete",
  ).length;
  const jumpTo = useCallback((slug: SectionSlug) => {
    setActive(slug);
    document.getElementById(slug)?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const collect = useCallback((values: Submission) => setCollected(values), []);

  return (
    <FormLayout>
      <FormNav
        statuses={statuses}
        complete={complete}
        active={active}
        onJump={jumpTo}
      />

      <FormProvider {...form}>
      <FormMain onSubmit={form.handleSubmit(collect)}>
        <GroupCrumbs groupId={groupId} />

        <PageHead>
          <PageTitle>Create atlas submission</PageTitle>
          <PageLead>
            Add the study details and observations you want to contribute.
          </PageLead>
        </PageHead>

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
                {...form.register("title")}
              />
            )}
          </Field>

          {/* Only once there is progress to report; an untouched form has
              nothing to say. */}
          {complete > 0 && (
            <ProgressBanner>
              <BannerStrong>
                {complete === SECTIONS.length
                  ? "Your submission is complete"
                  : `${complete} of ${SECTIONS.length} sections complete`}
              </BannerStrong>
              Required fields are marked with an asterisk. You can return to
              this draft at any time.
            </ProgressBanner>
          )}
        </FormIntro>

        {SECTIONS.map(({ slug, label }, i) => (
          <FormSection
            key={slug}
            slug={slug}
            title={label}
            step={i + 1}
            isActive={slug === active}
          >
            {SECTION_BODIES[slug](groupId)}
          </FormSection>
        ))}

        {collected && (
          <CollectedValues>{JSON.stringify(collected, null, 2)}</CollectedValues>
        )}

        <FormActions />
      </FormMain>
      </FormProvider>
    </FormLayout>
  );
};

export default SubmissionForm;
