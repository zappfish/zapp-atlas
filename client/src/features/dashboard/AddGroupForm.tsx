import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { useCreateGroup } from "@/api/hooks";
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

/** Name is the only field; the caller becomes the group's first admin. */
const AddGroupForm = ({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) => {
  const [name, setName] = useState("");
  const createGroup = useCreateGroup();
  const navigate = useNavigate();

  const close = () => {
    createGroup.reset();
    setName("");
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    createGroup.mutate(name.trim(), {
      onSuccess: (group) => {
        close();
        if (group) navigate(`/research-groups/${group.id}`);
      },
    });
  };

  return (
    <Modal open={open} title="Create research group" onClose={close}>
      <ModalForm onSubmit={submit}>
        <ModalTitle>Create research group</ModalTitle>

        <ModalField>
          <ModalLabel>Name</ModalLabel>
          <ModalInput
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            autoFocus
            maxLength={200}
            placeholder="e.g. Neurotoxicology Lab"
          />
        </ModalField>

        {createGroup.error && (
          <ModalText role="alert">{createGroup.error.message}</ModalText>
        )}

        <ModalActions>
          <button className="btn btn--neutral" type="button" onClick={close}>
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="submit"
            disabled={createGroup.isPending}
          >
            {createGroup.isPending ? "Creating…" : "Create"}
          </button>
        </ModalActions>
      </ModalForm>
    </Modal>
  );
};

export default AddGroupForm;
