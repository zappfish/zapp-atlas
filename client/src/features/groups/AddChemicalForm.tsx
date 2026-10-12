import { useState, type FormEvent } from "react";
import { useAddChemical } from "@/api/hooks";
import Modal from "@/components/Modal";

const AddChemicalForm = ({
  groupId,
  open,
  onClose,
}: {
  groupId: number;
  open: boolean;
  onClose: () => void;
}) => {
  const [chemicalId, setChemicalId] = useState("");
  const addChemical = useAddChemical(groupId);

  const close = () => {
    addChemical.reset();
    setChemicalId("");
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    addChemical.mutate(chemicalId.trim(), { onSuccess: close });
  };

  return (
    <Modal open={open} title="Add chemical" onClose={close}>
      <form className="modal__panel" onSubmit={submit}>
        <h2 className="modal__title">Add chemical</h2>

        <label className="modal__field">
          <span className="modal__label">Chemical id</span>
          <input
            className="modal__input"
            value={chemicalId}
            onChange={(e) => setChemicalId(e.target.value)}
            required
            autoFocus
            maxLength={60}
            placeholder="e.g. CHEBI:16236"
          />
        </label>

        {addChemical.error && (
          <p className="modal__text" role="alert">
            {addChemical.error.message}
          </p>
        )}

        <div className="modal__actions">
          <button className="btn btn--neutral" type="button" onClick={close}>
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="submit"
            disabled={addChemical.isPending}
          >
            {addChemical.isPending ? "Adding…" : "Add"}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default AddChemicalForm;
