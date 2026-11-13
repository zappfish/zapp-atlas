import { useState, type FormEvent } from "react";
import { useAddFish, useWildtypes } from "@/api/hooks";
import Modal from "@/components/Modal";
import {
  ModalActions,
  ModalField,
  ModalForm,
  ModalInput,
  ModalLabel,
  ModalSelect,
  ModalText,
  ModalTitle,
} from "@/styles/elements";

/**
 * A fish line is described, not named: its wild-type background, and later
 * the alleles it carries. The form takes the background for now; alleles
 * come with the fish picker. A nickname is what the group will pick it by.
 */
const AddFishForm = ({
  groupId,
  open,
  onClose,
}: {
  groupId: number;
  open: boolean;
  onClose: () => void;
}) => {
  const [background, setBackground] = useState("");
  const [nickname, setNickname] = useState("");
  const wildtypes = useWildtypes();
  const addFish = useAddFish(groupId);

  const close = () => {
    addFish.reset();
    setBackground("");
    setNickname("");
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const line = wildtypes.data?.find((w) => w.genotype_id === background);
    if (!line) return;
    addFish.mutate(
      {
        fish: {
          background_zfin_id: line.genotype_id,
          background_name: line.abbreviation,
        },
        nickname: nickname.trim() || null,
      },
      { onSuccess: close },
    );
  };

  return (
    <Modal open={open} title="Add fish line" onClose={close}>
      <ModalForm onSubmit={submit}>
        <ModalTitle>Add fish line</ModalTitle>

        <ModalField>
          <ModalLabel>Wild-type background</ModalLabel>
          <ModalSelect
            value={background}
            onChange={(e) => setBackground(e.target.value)}
            required
            autoFocus
            disabled={!wildtypes.data}
          >
            <option value="" disabled>
              {wildtypes.error
                ? "ZFIN's wild-type lines are not available"
                : wildtypes.data
                  ? "Choose a line"
                  : "Loading…"}
            </option>
            {wildtypes.data?.map((w) => (
              <option key={w.genotype_id} value={w.genotype_id}>
                {w.name}
              </option>
            ))}
          </ModalSelect>
        </ModalField>

        <ModalField>
          <ModalLabel>Nickname (optional)</ModalLabel>
          <ModalInput
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            maxLength={200}
            placeholder="What this group calls the line"
          />
        </ModalField>

        {addFish.error && (
          <ModalText role="alert">{addFish.error.message}</ModalText>
        )}

        <ModalActions>
          <button className="btn btn--neutral" type="button" onClick={close}>
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="submit"
            disabled={addFish.isPending || !wildtypes.data}
          >
            {addFish.isPending ? "Adding…" : "Add"}
          </button>
        </ModalActions>
      </ModalForm>
    </Modal>
  );
};

export default AddFishForm;
