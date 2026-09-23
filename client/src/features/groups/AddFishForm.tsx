import { useState, type FormEvent } from "react";
import { useAddFish } from "@/api/hooks";
import Modal from "@/components/Modal";

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
      <form className="modal__panel" onSubmit={submit}>
        <h2 className="modal__title">Add fish line</h2>

        <label className="modal__field">
          <span className="modal__label">ZFIN id</span>
          <input
            className="modal__input"
            value={zfinId}
            onChange={(e) => setZfinId(e.target.value)}
            required
            autoFocus
            placeholder="ZFIN:ZDB-GENO-960809-7"
            pattern={ZFIN_PATTERN}
            title="e.g. ZFIN:ZDB-GENO-960809-7"
          />
        </label>

        <label className="modal__field">
          <span className="modal__label">Name</span>
          <input
            className="modal__input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            maxLength={200}
            placeholder="e.g. AB"
          />
        </label>

        {addFish.error && (
          <p className="modal__text" role="alert">
            {addFish.error.message}
          </p>
        )}

        <div className="modal__actions">
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
        </div>
      </form>
    </Modal>
  );
};

export default AddFishForm;
