import { useCallback, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router";
import { ApiError } from "@/api/client";
import { useGroup, useSaveExperiment, useStudy } from "@/api/hooks";
import type { Experiment, Study } from "@/api/types";
import { bodyResolver, showProblems } from "@/problems";
import { sameBody, toBody, type Body } from "@/schema/bodies";
import {
  AddButton,
  AddRow,
  CrumbSeparator,
  Crumbs,
  EmptyText,
  FormLayout,
  FormMain,
  FormPart,
  PageHead,
  PageLead,
  PageTitle,
} from "@/styles/elements";
import { sectionStatuses } from "./status";
import FormActions from "./FormActions";
import FormNav from "./FormNav";
import FormSection from "./FormSection";
import ExposureEventCard from "./ExposureEventCard";
import ControlSection from "./sections/ControlSection";
import { Rearing } from "./sections/ExperimentSection";
import FishSection from "./sections/FishSection";
import { SECTIONS, type SectionSlug } from "./sections";
import "./form.css";

type Values = Body<"Experiment">;

/** What a new experiment starts with: standard rearing, and one control to fill in. */
const BLANK: Values = { standard_rearing_condition: true, control: [{}] };

/**
 * The experiment's own fields as a body, with a control to fill in if it has
 * none. Its exposure events are saved on their own.
 */
const ownFields = (saved: Experiment): Values => {
  const body = toBody("Experiment", { ...saved, exposure_event: undefined });
  return { ...body, control: body.control?.length ? body.control : [{}] };
};

const studyName = (study: Study) =>
  study.nickname ?? study.publication ?? "Study";

/** Where the experiment sits: its group, then its study. */
const StudyCrumbs = ({
  groupId,
  study,
  here,
}: {
  groupId: number;
  study: Study;
  here: string;
}) => {
  const { data: group } = useGroup(groupId);

  return (
    <Crumbs aria-label="Breadcrumb">
      <Link to={`/research-groups/${groupId}`}>{group?.name ?? "Group"}</Link>
      <CrumbSeparator aria-hidden="true">›</CrumbSeparator>
      <Link to={`/research-groups/${groupId}/studies/${study.id}`}>
        {studyName(study)}
      </Link>
      <CrumbSeparator aria-hidden="true">›</CrumbSeparator>
      <span aria-current="page">{here}</span>
    </Crumbs>
  );
};

/** The experiment's exposure events, each saved on its own. */
const ExposureEvents = ({
  groupId,
  studyId,
  experiment,
}: {
  groupId: number;
  studyId: number;
  experiment: Experiment;
}) => {
  const saved = experiment.exposure_event ?? [];
  // Events added on this visit and not saved yet, by a key of their own.
  const [unsaved, setUnsaved] = useState<number[]>([]);
  const [next, setNext] = useState(0);

  const add = () => {
    setUnsaved((keys) => [...keys, next]);
    setNext(next + 1);
  };
  const leave = (key: number) =>
    setUnsaved((keys) => keys.filter((each) => each !== key));

  return (
    <>
      {saved.length + unsaved.length === 0 && (
        <EmptyText>
          No exposure events yet. Add one for each group of fish and what it
          was exposed to.
        </EmptyText>
      )}

      {saved.map((exposure, i) => (
        <ExposureEventCard
          key={exposure.id}
          n={i + 1}
          groupId={groupId}
          studyId={studyId}
          experimentId={experiment.id}
          saved={exposure}
        />
      ))}

      {unsaved.map((key, i) => (
        <ExposureEventCard
          key={`new-${key}`}
          n={saved.length + i + 1}
          groupId={groupId}
          studyId={studyId}
          experimentId={experiment.id}
          onLeave={() => leave(key)}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={add}>
          + Add an exposure event
        </AddButton>
      </AddRow>
    </>
  );
};

const Loaded = ({
  groupId,
  study,
  saved,
}: {
  groupId: number;
  study: Study;
  /** Absent for an experiment that has not been saved yet. */
  saved?: Experiment;
}) => {
  // The first section, whatever the order in sections.ts says it is.
  const [active, setActive] = useState<SectionSlug>(SECTIONS[0].slug);
  const navigate = useNavigate();
  const save = useSaveExperiment(study.id, saved?.id ?? null);
  const form = useForm<Values>({
    values: saved ? ownFields(saved) : BLANK,
    resolver: bodyResolver("Experiment"),
    // Checked on leaving a field, then as it is corrected.
    mode: "onTouched",
  });

  // Watched, so a dot answers to what has been entered rather than to a save.
  const entered = form.watch();
  const statuses = sectionStatuses(entered, saved?.exposure_event?.length ?? 0);
  // Whether saving would change anything, which is what the form's own
  // "dirty" flag is not: it stays set after saved values come back.
  const isSaved = saved && sameBody("Experiment", entered, ownFields(saved));
  // Read off those statuses, so the summary and the dots cannot disagree.
  const complete = Object.values(statuses).filter(
    (status) => status === "complete",
  ).length;
  const jumpTo = useCallback((slug: SectionSlug) => {
    setActive(slug);
    document.getElementById(slug)?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const here = `/research-groups/${groupId}/studies/${study.id}/experiments`;
  const submit = form.handleSubmit((values) =>
    save.mutate(toBody("Experiment", values), {
      // A new experiment's page is now the one named for it.
      onSuccess: (stored) => {
        if (!saved && stored) navigate(`${here}/${stored.id}`, { replace: true });
      },
      // Anything the server found that the schema could not say.
      onError: (error) => {
        if (error instanceof ApiError) showProblems(form.setError, error.problems);
      },
    }),
  );

  const [fish, experiment, control, exposures] = SECTIONS;

  return (
    <FormLayout>
      <FormNav
        statuses={statuses}
        complete={complete}
        active={active}
        onJump={jumpTo}
      />

      <FormMain>
        <StudyCrumbs
          groupId={groupId}
          study={study}
          here={saved ? "Experiment" : "New experiment"}
        />

        <PageHead>
          <PageTitle>{saved ? "Experiment" : "New experiment"}</PageTitle>
          <PageLead>
            Describe the fish and how they were kept, then each group of fish
            and what it was exposed to.
          </PageLead>
        </PageHead>

        <FormProvider {...form}>
          <FormPart onSubmit={submit} aria-label="Experiment">
            <FormSection
              slug={fish.slug}
              title={fish.label}
              step={1}
              isActive={active === fish.slug}
            >
              <FishSection groupId={groupId} />
            </FormSection>

            <FormSection
              slug={experiment.slug}
              title={experiment.label}
              step={2}
              isActive={active === experiment.slug}
            >
              <Rearing />
            </FormSection>

            <FormSection
              slug={control.slug}
              title={control.label}
              step={3}
              isActive={active === control.slug}
            >
              <ControlSection />
            </FormSection>

            <FormActions
              title={saved ? "Fish, rearing and controls" : "Save to continue"}
              hint={
                save.error
                  ? save.error.message
                  : !saved
                    ? "Exposure events are added once the experiment is saved."
                    : isSaved
                      ? "Saved."
                      : "Changes not saved."
              }
              label="Save experiment"
              isPending={save.isPending}
            />
          </FormPart>
        </FormProvider>

        <FormSection
          slug={exposures.slug}
          title={exposures.label}
          step={4}
          isActive={active === exposures.slug}
        >
          {saved ? (
            <ExposureEvents
              groupId={groupId}
              studyId={study.id}
              experiment={saved}
            />
          ) : (
            <EmptyText>
              Save the experiment to add its exposure events.
            </EmptyText>
          )}
        </FormSection>
      </FormMain>
    </FormLayout>
  );
};

/**
 * One experiment of a study: the fish, how they were kept and the controls,
 * saved together, and beneath them its exposure events.
 */
const ExperimentForm = ({
  groupId,
  studyId,
  experimentId,
}: {
  groupId: number;
  studyId: number;
  /** Null for an experiment being created. */
  experimentId: number | null;
}) => {
  const { data: study, error } = useStudy(studyId);

  if (error) return <p>This study is not available.</p>;
  if (!study) return null;
  if (experimentId === null) return <Loaded groupId={groupId} study={study} />;

  const saved = study.experiment?.find((each) => each.id === experimentId);
  if (!saved) return <p>This experiment is not available.</p>;
  // Keyed, so going from one experiment to another starts a fresh form.
  return <Loaded key={saved.id} groupId={groupId} study={study} saved={saved} />;
};

export default ExperimentForm;
