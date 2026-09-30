import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { useCreateGroup } from "@/api/hooks";
import Modal from "@/components/Modal";

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
      <form className="modal__panel" onSubmit={submit}>
        <h2 className="modal__title">Create research group</h2>

        <label className="modal__field">
          <span className="modal__label">Name</span>
          <input
            className="modal__input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            autoFocus
            maxLength={200}
            placeholder="e.g. Neurotoxicology Lab"
          />
        </label>

        {createGroup.error && (
          <p className="modal__text" role="alert">
            {createGroup.error.message}
          </p>
        )}

        <div className="modal__actions">
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
        </div>
      </form>
    </Modal>
  );
};

export default AddGroupForm;
