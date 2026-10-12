import { useEffect, useState, type FormEvent } from "react";
import { useUpdateChemical } from "@/api/hooks";
import Modal from "@/components/Modal";
import type { Row } from "@/components/RecordSection";

const EditChemicalForm = ({
  groupId,
  entry,
  onClose,
}: {
  groupId: number;
  /** The row being edited, or null when the dialog is closed. */
  entry: Row | null;
  onClose: () => void;
}) => {
  const [chemicalId, setChemicalId] = useState("");
  const updateChemical = useUpdateChemical(groupId);

  // Prefill from whichever row opened it.
  useEffect(() => {
    if (entry) setChemicalId(entry.label);
  }, [entry]);

  const close = () => {
    updateChemical.reset();
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!entry) return;
    updateChemical.mutate(
      { entryId: entry.id, chemicalId: chemicalId.trim() },
      { onSuccess: close },
    );
  };

  return (
    <Modal open={entry !== null} title="Edit chemical" onClose={close}>
      <form className="modal__panel" onSubmit={submit}>
        <h2 className="modal__title">Edit chemical</h2>

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

        {updateChemical.error && (
          <p className="modal__text" role="alert">
            {updateChemical.error.message}
          </p>
        )}

        <div className="modal__actions">
          <button className="btn btn--neutral" type="button" onClick={close}>
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="submit"
            disabled={updateChemical.isPending}
          >
            {updateChemical.isPending ? "Saving…" : "Save"}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default EditChemicalForm;
