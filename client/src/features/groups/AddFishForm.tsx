import { useState, type FormEvent } from "react";
import { useAddFish } from "@/api/hooks";
import Modal from "@/components/Modal";
import {
  ModalActions,
  ModalField,
  ModalForm,
  ModalInput,
  ModalLabel,
  ModalText,
  ModalTitle,
} from "@/styles/elements";

/** Matches the schema's zfin_id pattern, which the API validates too. */
const ZFIN_PATTERN = "ZFIN:ZDB-[A-Z]+-\\d{6}-\\d+";

const AddFishForm = ({
  groupId,
  open,
  onClose,
}: {
  groupId: number;
  open: boolean;
  onClose: () => void;
}) => {
  const [zfinId, setZfinId] = useState("");
  const [name, setName] = useState("");
  const addFish = useAddFish(groupId);

  const close = () => {
    addFish.reset();
    setZfinId("");
    setName("");
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    addFish.mutate(
      { zfin_id: zfinId.trim(), name: name.trim() },
      { onSuccess: close },
    );
  };

  return (
    <Modal open={open} title="Add fish line" onClose={close}>
      <ModalForm onSubmit={submit}>
        <ModalTitle>Add fish line</ModalTitle>

        <ModalField>
          <ModalLabel>ZFIN id</ModalLabel>
          <ModalInput
            value={zfinId}
            onChange={(e) => setZfinId(e.target.value)}
            required
            autoFocus
            placeholder="ZFIN:ZDB-GENO-960809-7"
            pattern={ZFIN_PATTERN}
            title="e.g. ZFIN:ZDB-GENO-960809-7"
          />
        </ModalField>

        <ModalField>
          <ModalLabel>Name</ModalLabel>
          <ModalInput
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            maxLength={200}
            placeholder="e.g. AB"
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
            disabled={addFish.isPending}
          >
            {addFish.isPending ? "Adding…" : "Add"}
          </button>
        </ModalActions>
      </ModalForm>
    </Modal>
  );
};

export default AddFishForm;
