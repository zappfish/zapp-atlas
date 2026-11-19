import { useCallback, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { ApiError } from "@/api/client";
import {
  useChemicalNames,
  useDeleteExposure,
  useSaveExposure,
} from "@/api/hooks";
import type { ExposureEvent } from "@/api/types";
import ConfirmDialog from "@/components/ConfirmDialog";
import { bodyResolver, showProblems, type Problem } from "@/problems";
import { sameBody, toBody, type Body } from "@/schema/bodies";
import {
  EntryActions,
  EntryCaret,
  EntryForm,
  EntryHead,
  EntryRemove,
  EntryStatus,
  GroupSummaryText,
  GroupToggle,
} from "@/styles/elements";
import { ExposureFields } from "./sections/ExperimentSection";
import { ZFS_STAGES } from "./stages";

type Values = Body<"ExposureEvent">;

/** What a new exposure event starts with: the commonest route, and its regimen. */
const BLANK: Values = {
  route: "aquatic_environment",
  regimen: { exposure_regimen_type: "continuous" },
};

/** The event's own fields as a body. Its observations are saved on their own. */
const ownFields = (saved: ExposureEvent): Values =>
  toBody("ExposureEvent", { ...saved, phenotype_observation: undefined });

const order = (stage: string | null | undefined) =>
  ZFS_STAGES.findIndex((each) => each.id === stage);

/** The schema holds each stage on its own; that one follows the other is said here. */
const stagesInOrder = (values: Values): Problem[] => {
  const start = order(values.exposure_start_stage);
  const end = order(values.exposure_end_stage);
  return start >= 0 && end >= 0 && end < start
    ? [
        {
          path: ["exposure_end_stage"],
          message: "Must not be before the start stage.",
        },
      ]
    : [];
};

/**
 * One exposure event of the experiment, saved on its own. Folded to a line
 * once saved, and opened to change it.
 */
const ExposureEventCard = ({
  n,
  groupId,
  studyId,
  experimentId,
  saved,
  onLeave,
}: {
  n: number;
  groupId: number;
  studyId: number;
  experimentId: number;
  /** Absent for an event that has not been saved yet. */
  saved?: ExposureEvent;
  /** An event that was never saved is discarded, or saved and listed anew. */
  onLeave?: () => void;
}) => {
  const [isOpen, setIsOpen] = useState(!saved);
  const [removing, setRemoving] = useState(false);
  const toggle = useCallback(() => setIsOpen((was) => !was), []);

  const save = useSaveExposure(studyId, experimentId, saved?.id ?? null);
  const remove = useDeleteExposure(studyId);
  const form = useForm<Values>({
    values: saved ? ownFields(saved) : BLANK,
    resolver: bodyResolver("ExposureEvent", stagesInOrder),
    // Checked on leaving a field, then as it is corrected.
    mode: "onTouched",
  });

  const entered = form.watch();
  const chemicalId = entered.stressor?.[0]?.chemical_id;
  const concentration = entered.stressor?.[0]?.concentration;
  // Whether saving would change anything.
  const isSaved = saved && sameBody("ExposureEvent", entered, ownFields(saved));
  const names = useChemicalNames(chemicalId ? [chemicalId] : []);
  // Only what has been filled in: an event with nothing entered says nothing.
  const summary = [
    chemicalId && (names.get(chemicalId) ?? chemicalId),
    concentration && `${concentration.numeric_value} ${concentration.unit ?? ""}`,
  ].filter(Boolean);

  const submit = form.handleSubmit((values) =>
    save.mutate(toBody("ExposureEvent", values), {
      onSuccess: () => {
        setIsOpen(false);
        onLeave?.();
      },
      // Anything the server found that the schema could not say.
      onError: (error) => {
        if (error instanceof ApiError) showProblems(form.setError, error.problems);
      },
    }),
  );

  return (
    <FormProvider {...form}>
      <EntryForm onSubmit={submit} aria-label={`Exposure event ${n}`}>
        <EntryHead>
          <GroupToggle type="button" onClick={toggle} aria-expanded={isOpen}>
            <EntryCaret aria-hidden="true" isOpen={isOpen}>
              ▶
            </EntryCaret>
            Exposure event {n}
          </GroupToggle>
          {summary.length > 0 && (
            <GroupSummaryText>{summary.join(" • ")}</GroupSummaryText>
          )}
          <EntryRemove
            type="button"
            onClick={saved ? () => setRemoving(true) : onLeave}
          >
            Remove
          </EntryRemove>
        </EntryHead>

        {isOpen && (
          <>
            <ExposureFields groupId={groupId} />

            <EntryActions>
              <EntryStatus role="status">
                {save.error
                  ? save.error.message
                  : !saved
                    ? "Not saved yet."
                    : isSaved
                      ? "Saved."
                      : "Changes not saved."}
              </EntryStatus>
              <button
                className="btn btn--primary"
                type="submit"
                disabled={save.isPending}
              >
                {save.isPending ? "Saving…" : "Save exposure event"}
              </button>
            </EntryActions>
          </>
        )}
      </EntryForm>

      {saved && (
        <ConfirmDialog
          open={removing}
          title="Remove exposure event"
          message={`Remove exposure event ${n} and the observations made of it?`}
          isPending={remove.isPending}
          error={remove.error?.message}
          onConfirm={() => remove.mutate(saved.id)}
          onClose={() => {
            remove.reset();
            setRemoving(false);
          }}
        />
      )}
    </FormProvider>
  );
};

export default ExposureEventCard;
