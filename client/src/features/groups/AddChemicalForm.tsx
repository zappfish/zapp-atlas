import { useMemo, useState } from "react";
import { useAddChemical, useCabinet } from "@/api/hooks";
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
  const addChemical = useAddChemical(groupId);
  const { data: cabinet = [] } = useCabinet(groupId);
  // A fresh Set each render would re-run what reads it.
  const alreadyIn = useMemo(
    () => new Set(cabinet.map((row) => row.chemical_id)),
    [cabinet],
  );

  const close = () => {
    addChemical.reset();
    setStaged([]);
    onClose();
  };

  const stage = (chemical: Staged) =>
    setStaged((was) =>
      was.some((each) => each.chebiId === chemical.chebiId)
        ? was
        : [...was, chemical],
    );

  const unstage = (chebiId: string) =>
    setStaged((was) => was.filter((each) => each.chebiId !== chebiId));

  // Sequential: a failure leaves the dialog open on the error.
  const save = async () => {
    for (const chemical of staged) {
      await addChemical.mutateAsync(chemical.chebiId);
    }
    close();
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
            onStage={stage}
          />

          {addChemical.error && (
            <ModalText role="alert">{addChemical.error.message}</ModalText>
          )}

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
                <StagedEmptyTitle>No chemicals selected yet</StagedEmptyTitle>
                <StagedEmptyText>
                  Search above to start building your list.
                </StagedEmptyText>
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
                    <StagedRemove
                      type="button"
                      onClick={() => unstage(chemical.chebiId)}
                      aria-label={`Remove ${chemical.name}`}
                    >
                      <TrashIcon />
                    </StagedRemove>
                  </StagedItem>
                ))}
              </StagedItems>
            )}
          </StagedList>
        </ModalBody>

        <ModalFoot>
          <button className="btn btn--secondary" type="button" onClick={close}>
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="button"
            onClick={save}
            disabled={staged.length === 0 || addChemical.isPending}
          >
            {addChemical.isPending
              ? "Adding…"
              : `Add ${staged.length} chemical${staged.length === 1 ? "" : "s"}`}
          </button>
        </ModalFoot>
      </ModalBanded>
    </Modal>
  );
};

export default AddChemicalForm;
