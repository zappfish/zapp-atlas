import { useCallback, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { ApiError } from "@/api/client";
import { useDeleteObservation, useSaveObservation } from "@/api/hooks";
import type { Observation } from "@/api/types";
import ConfirmDialog from "@/components/ConfirmDialog";
import { bodyResolver, showProblems, type Problem } from "@/problems";
import { sameBody, toBody, type Body } from "@/schema/bodies";
import {
  EmptyText,
  EntryActions,
  EntryCaret,
  EntryCard,
  EntryHead,
  EntryList,
  EntryListAdd,
  EntryListHead,
  EntryNested,
  EntryPart,
  EntryRemove,
  EntryStatus,
  EntryTitle,
  GroupSummaryText,
  GroupToggle,
} from "@/styles/elements";
import ImageCard from "./ImageCard";
import PhenotypeFields from "./sections/PhenotypeSection";
import { ZFS_STAGES, stageSpan } from "./stages";

type Values = Body<"PhenotypeObservationSet">;

/** What a new observation starts with: one phenotype to fill in. */
const BLANK: Values = { phenotype: [{}] };

/**
 * The observation's own fields as a body, with a phenotype to fill in if it
 * has none. Its images are saved on their own.
 */
const ownFields = (saved: Observation): Values => {
  const body = toBody("PhenotypeObservationSet", { ...saved, image: undefined });
  return { ...body, phenotype: body.phenotype?.length ? body.phenotype : [{}] };
};

/** The schema asks nothing of a phenotype; the guidelines ask for the fish's age. */
const stagesGiven = (values: Values): Problem[] =>
  (values.phenotype ?? []).flatMap((phenotype, i) =>
    Object.keys(toBody("Phenotype", phenotype)).length > 0 && !phenotype.stage
      ? [
          {
            path: ["phenotype", i, "stage"],
            message: "Enter the stage the phenotype was seen at.",
          },
        ]
      : [],
  );

const count = (n: number, one: string) => `${n} ${one}${n === 1 ? "" : "s"}`;

/**
 * The observation's images, each uploaded and described on its own. They
 * come first in the card: the phenotypes recorded are the ones they show.
 */
const Images = ({
  studyId,
  observation,
}: {
  studyId: number;
  /** Absent until the observation is saved, which an image is uploaded to. */
  observation?: Observation;
}) => {
  const saved = observation?.image ?? [];
  // Images added on this visit and not uploaded yet, by a key of their own.
  const [unsaved, setUnsaved] = useState<number[]>([]);
  const [next, setNext] = useState(0);

  const add = () => {
    setUnsaved((keys) => [...keys, next]);
    setNext(next + 1);
  };
  const leave = (key: number) =>
    setUnsaved((keys) => keys.filter((each) => each !== key));

  if (!observation) {
    return (
      <EntryList>
        <EntryListHead>
          <EntryTitle>Images</EntryTitle>
        </EntryListHead>
        <EmptyText>Images are added once the observation is saved.</EmptyText>
      </EntryList>
    );
  }

  return (
    <EntryList>
      <EntryListHead>
        <EntryTitle>Images</EntryTitle>
        <EntryListAdd type="button" onClick={add}>
          + Add an image
        </EntryListAdd>
      </EntryListHead>

      {saved.length + unsaved.length === 0 && (
        <EmptyText>No images of this observation yet.</EmptyText>
      )}

      {saved.map((image, i) => (
        <ImageCard
          key={image.id}
          n={i + 1}
          studyId={studyId}
          observationId={observation.id}
          saved={image}
        />
      ))}

      {unsaved.map((key, i) => (
        <ImageCard
          key={`new-${key}`}
          n={saved.length + i + 1}
          studyId={studyId}
          observationId={observation.id}
          onLeave={() => leave(key)}
        />
      ))}
    </EntryList>
  );
};

/**
 * One observation of an exposure event: its images, and the phenotypes they
 * show. The phenotypes are saved as the observation, and each image on its
 * own once there is an observation to upload it to.
 */
const ObservationCard = ({
  n,
  studyId,
  exposureId,
  saved,
  onLeave,
}: {
  n: number;
  studyId: number;
  exposureId: number;
  /** Absent for an observation that has not been saved yet. */
  saved?: Observation;
  /** An observation that was never saved is discarded, or saved and listed anew. */
  onLeave?: () => void;
}) => {
  const [isOpen, setIsOpen] = useState(!saved);
  const [removing, setRemoving] = useState(false);
  const toggle = useCallback(() => setIsOpen((was) => !was), []);

  const save = useSaveObservation(studyId, exposureId, saved?.id ?? null);
  const remove = useDeleteObservation(studyId);
  const form = useForm<Values>({
    values: saved ? ownFields(saved) : BLANK,
    resolver: bodyResolver("PhenotypeObservationSet", stagesGiven),
    // Checked on leaving a field, then as it is corrected.
    mode: "onTouched",
  });

  const entered = form.watch();
  // Whether saving would change anything.
  const isSaved =
    saved && sameBody("PhenotypeObservationSet", entered, ownFields(saved));
  // Named for when it was made and what was seen, once those are entered.
  const phenotypes = entered.phenotype ?? [];
  const stages = [...new Set(phenotypes.map((each) => each.stage))].flatMap(
    (id) => ZFS_STAGES.filter((stage) => stage.id === id).map(stageSpan),
  );
  const terms = phenotypes.flatMap((each) => {
    const term = each.phenotype_term_id;
    return term ? [term.term_label ?? term.term_uri] : [];
  });
  const title = [...stages, ...terms].join(" • ");
  // Its number is the lesser label, with how many images it has once saved.
  const label = [
    ...(title ? [`Observation ${n}`] : []),
    ...(saved ? [count(saved.image?.length ?? 0, "image")] : []),
  ];

  const submit = form.handleSubmit((values) =>
    save.mutate(toBody("PhenotypeObservationSet", values), {
      onSuccess: onLeave,
      // Anything the server found that the schema could not say.
      onError: (error) => {
        if (error instanceof ApiError) showProblems(form.setError, error.problems);
      },
    }),
  );

  return (
    <EntryCard role="group" aria-label={`Observation ${n}`}>
      <EntryHead>
        <GroupToggle type="button" onClick={toggle} aria-expanded={isOpen}>
          <EntryCaret aria-hidden="true" isOpen={isOpen}>
            ▶
          </EntryCaret>
          {title || `Observation ${n}`}
        </GroupToggle>
        {label.length > 0 && (
          <GroupSummaryText>{label.join(" • ")}</GroupSummaryText>
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
          <Images studyId={studyId} observation={saved} />

          <FormProvider {...form}>
            <EntryPart onSubmit={submit}>
              <PhenotypeFields />

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
                  {save.isPending ? "Saving…" : "Save observation"}
                </button>
              </EntryActions>
            </EntryPart>
          </FormProvider>
        </>
      )}

      {/* Inside the card, so that one card still directly follows another. */}
      {saved && (
        <ConfirmDialog
          open={removing}
          title="Remove observation"
          message={`Remove observation ${n} and its images?`}
          isPending={remove.isPending}
          error={remove.error?.message}
          onConfirm={() => remove.mutate(saved.id)}
          onClose={() => {
            remove.reset();
            setRemoving(false);
          }}
        />
      )}
    </EntryCard>
  );
};

/** What was seen of an exposure event's fish, one observation to a look. */
export const Observations = ({
  studyId,
  exposureId,
  saved,
}: {
  studyId: number;
  exposureId: number;
  saved: Observation[];
}) => {
  // Observations added on this visit and not saved yet, by a key of their own.
  const [unsaved, setUnsaved] = useState<number[]>([]);
  const [next, setNext] = useState(0);

  const add = () => {
    setUnsaved((keys) => [...keys, next]);
    setNext(next + 1);
  };
  const leave = (key: number) =>
    setUnsaved((keys) => keys.filter((each) => each !== key));

  return (
    <EntryNested>
      <EntryListHead>
        <EntryTitle>Observations</EntryTitle>
        <EntryListAdd type="button" onClick={add}>
          + Add an observation
        </EntryListAdd>
      </EntryListHead>

      {saved.length + unsaved.length === 0 && (
        <EmptyText>No observations of this exposure event yet.</EmptyText>
      )}

      {saved.map((observation, i) => (
        <ObservationCard
          key={observation.id}
          n={i + 1}
          studyId={studyId}
          exposureId={exposureId}
          saved={observation}
        />
      ))}

      {unsaved.map((key, i) => (
        <ObservationCard
          key={`new-${key}`}
          n={saved.length + i + 1}
          studyId={studyId}
          exposureId={exposureId}
          onLeave={() => leave(key)}
        />
      ))}
    </EntryNested>
  );
};

export default ObservationCard;
