import { useCallback, useState } from "react";
import { useAddFish } from "@/api/hooks";
import type { FishBody, FishTankEntry } from "@/api/types";
import Modal from "@/components/Modal";
import FishBuilder from "@/features/fish/FishBuilder";
import {
  ModalBanded,
  ModalBody,
  ModalField,
  ModalFoot,
  ModalHead,
  ModalInput,
  ModalLabel,
  ModalText,
  ModalTitle,
} from "@/styles/elements";

/**
 * Adds a line to the group's tank: background, alleles with zygosity, notes,
 * and an optional nickname the group picks it by. The ZFIN ids come from the
 * resolve result.
 */
const AddFishForm = ({
  groupId,
  open,
  onClose,
  onAdded,
}: {
  groupId: number;
  open: boolean;
  onClose: () => void;
  /** The saved entry, for a caller that wants to pick it straight away. */
  onAdded?: (entry: FishTankEntry) => void;
}) => {
  const [fish, setFish] = useState<FishBody | null>(null);
  const [nickname, setNickname] = useState("");
  const addFish = useAddFish(groupId);
  const onChange = useCallback((next: FishBody | null) => setFish(next), []);

  const close = () => {
    addFish.reset();
    setFish(null);
    setNickname("");
    onClose();
  };

  const save = () => {
    if (!fish) return;
    addFish.mutate(
      { fish, nickname: nickname.trim() || null },
      {
        onSuccess: (entry) => {
          if (entry) onAdded?.(entry);
          close();
        },
      },
    );
  };

  return (
    <Modal open={open} title="Add fish line" onClose={close} isWide>
      <ModalBanded>
        <ModalHead>
          <ModalTitle>Add fish line</ModalTitle>
          <ModalText>
            Choose the background and add the alleles the line carries. If ZFIN has a
            registered fish with this description, its ids are stored with the entry.
          </ModalText>
        </ModalHead>

        <ModalBody>
          <FishBuilder isDisabled={addFish.isPending} onChange={onChange} />

          <ModalField>
            <ModalLabel>Nickname (optional)</ModalLabel>
            <ModalInput
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              maxLength={200}
              placeholder="What this group calls the line"
              disabled={addFish.isPending}
            />
          </ModalField>

          {addFish.error && <ModalText role="alert">{addFish.error.message}</ModalText>}
        </ModalBody>

        <ModalFoot>
          <button
            className="btn btn--secondary"
            type="button"
            onClick={close}
            disabled={addFish.isPending}
          >
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="button"
            onClick={save}
            disabled={!fish || addFish.isPending}
          >
            {addFish.isPending ? "Adding…" : "Add to tank"}
          </button>
        </ModalFoot>
      </ModalBanded>
    </Modal>
  );
};

export default AddFishForm;
