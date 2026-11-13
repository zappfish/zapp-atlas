import { useState } from "react";
import { useAddChemical, useCabinet, useRefreshCabinet } from "@/api/hooks";
import Modal from "@/components/Modal";
import ChemicalPicker, { type Staged } from "./ChemicalPicker";
import { FlaskIcon, TrashIcon } from "@/components/icons";
import {
  ModalBanded,
  ModalBody,
  ModalFoot,
  ModalHead,
  ModalText,
  ModalTitle,
  Staged as StagedList,
  StagedCount,
  StagedEmpty,
  StagedEmptyCopy,
  StagedEmptyIcon,
  StagedEmptyText,
  StagedEmptyTitle,
  StagedHead,
  StagedId,
  StagedItem,
  StagedLead,
  StagedList as StagedItems,
  StagedName,
  StagedNames,
  StagedError,
  StagedNickname,
  StagedNumber,
  StagedRemove,
  StagedTitle,
} from "@/styles/elements";

/** Staged at once. */
const LIMIT = 5;

/** Staged first, so several can be looked over together before any is saved. */
const AddChemicalForm = ({
  groupId,
  open,
  onClose,
}: {
  groupId: number;
  open: boolean;
  onClose: () => void;
}) => {
  const [staged, setStaged] = useState<Staged[]>([]);
  const [nicknames, setNicknames] = useState<Record<string, string>>({});
  // Why each one that would not save was refused, against its identifier.
  const [failures, setFailures] = useState<Record<string, string>>({});
  // Covers the whole loop: isPending falls between one chemical and the next.
  const [isSaving, setIsSaving] = useState(false);
  const addChemical = useAddChemical(groupId);
  const refreshCabinet = useRefreshCabinet(groupId);
  const { data: cabinet = [] } = useCabinet(groupId);
  const alreadyIn = new Set(cabinet.map((row) => row.chemical_id));

  const close = () => {
    addChemical.reset();
    setStaged([]);
    setNicknames({});
    setFailures({});
    onClose();
  };

  const rename = (chebiId: string, nickname: string) => {
    setNicknames((was) => ({ ...was, [chebiId]: nickname }));
    setFailures((was) =>
      Object.fromEntries(Object.entries(was).filter(([id]) => id !== chebiId)),
    );
  };

  const stage = (chemical: Staged) =>
    setStaged((was) =>
      was.some((each) => each.chebiId === chemical.chebiId)
        ? was
        : [...was, chemical],
    );

  const unstage = (chebiId: string) =>
    setStaged((was) => was.filter((each) => each.chebiId !== chebiId));

  // Each is independent, so one refusal does not hold up the rest: those that
  // save are dropped, and those that cannot keep their reason and their row.
  const save = async () => {
    const refused: Record<string, string> = {};
    setIsSaving(true);
    setFailures({});

    for (const chemical of staged) {
      try {
        await addChemical.mutateAsync({
          chemicalId: chemical.chebiId,
          nickname: nicknames[chemical.chebiId]?.trim() || undefined,
        });
        setStaged((was) =>
          was.filter((each) => each.chebiId !== chemical.chebiId),
        );
      } catch (error) {
        refused[chemical.chebiId] =
          error instanceof Error ? error.message : "Could not be added";
      }
    }

    setFailures(refused);
    setIsSaving(false);
    await refreshCabinet();
    if (Object.keys(refused).length === 0) close();
  };

  return (
    <Modal open={open} title="Add chemicals" onClose={close} isWide>
      <ModalBanded>
        <ModalHead>
          <ModalTitle>Add chemicals</ModalTitle>
          <ModalText>
            Search ChEBI by name or identifier, and add up to {LIMIT} at a time.
          </ModalText>
        </ModalHead>

        <ModalBody>
          <ChemicalPicker
            staged={staged}
            limit={LIMIT}
            alreadyIn={alreadyIn}
            isDisabled={isSaving}
            onPick={stage}
          />

          <StagedList>
            <StagedHead>
              <StagedTitle>Ready to add</StagedTitle>
              <StagedCount>
                {staged.length} / {LIMIT}
              </StagedCount>
            </StagedHead>
            <StagedLead>
              {staged.length === 0
                ? "Your selected chemicals will appear here."
                : "These chemicals will be added to the cabinet."}
            </StagedLead>

            {staged.length === 0 ? (
              <StagedEmpty>
                <StagedEmptyIcon aria-hidden="true">
                  <FlaskIcon />
                </StagedEmptyIcon>
                <StagedEmptyCopy>
                  <StagedEmptyTitle>No chemicals selected yet</StagedEmptyTitle>
                  <StagedEmptyText>
                    Search above to start building your list.
                  </StagedEmptyText>
                </StagedEmptyCopy>
              </StagedEmpty>
            ) : (
              <StagedItems>
                {staged.map((chemical, i) => (
                  <StagedItem key={chemical.chebiId}>
                    <StagedNumber aria-hidden="true">{i + 1}</StagedNumber>
                    <StagedNames>
                      <StagedName>{chemical.name}</StagedName>
                      <StagedId>{chemical.chebiId}</StagedId>
                    </StagedNames>
                    <StagedNickname
                      value={nicknames[chemical.chebiId] ?? ""}
                      onChange={(e) => rename(chemical.chebiId, e.target.value)}
                      placeholder="Nickname (optional)"
                      aria-label={`Nickname for ${chemical.name}`}
                      maxLength={60}
                      disabled={isSaving}
                    />
                    <StagedRemove
                      type="button"
                      onClick={() => unstage(chemical.chebiId)}
                      aria-label={`Remove ${chemical.name}`}
                      disabled={isSaving}
                    >
                      <TrashIcon />
                    </StagedRemove>
                    {/* Last, so the grid places it on the line below rather
                        than pushing the controls after it onto one. */}
                    {failures[chemical.chebiId] && (
                      <StagedError role="alert">
                        {failures[chemical.chebiId]}
                      </StagedError>
                    )}
                  </StagedItem>
                ))}
              </StagedItems>
            )}
          </StagedList>
        </ModalBody>

        <ModalFoot>
          <button
            className="btn btn--secondary"
            type="button"
            onClick={close}
            disabled={isSaving}
          >
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="button"
            onClick={save}
            disabled={staged.length === 0 || isSaving}
          >
            {isSaving
              ? "Adding…"
              : `Add ${staged.length} chemical${staged.length === 1 ? "" : "s"}`}
          </button>
        </ModalFoot>
      </ModalBanded>
    </Modal>
  );
};

export default AddChemicalForm;
