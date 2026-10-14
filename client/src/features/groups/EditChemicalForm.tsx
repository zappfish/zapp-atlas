import { useEffect, useState, type FormEvent } from "react";
import { useUpdateChemical } from "@/api/hooks";
import Modal from "@/components/Modal";
import type { Row } from "@/components/RecordSection";
import {
  ModalActions,
  ModalField,
  ModalForm,
  ModalInput,
  ModalLabel,
  ModalText,
  ModalTitle,
} from "@/styles/elements";

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
  const [nickname, setNickname] = useState("");
  const updateChemical = useUpdateChemical(groupId);

  // Prefill from whichever row opened it.
  useEffect(() => {
    if (!entry) return;
    setChemicalId(entry.label);
    setNickname(entry.sublabel ?? "");
  }, [entry]);

  const close = () => {
    updateChemical.reset();
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!entry) return;
    updateChemical.mutate(
      {
        entryId: entry.id,
        chemicalId: chemicalId.trim(),
        // Cleared rather than left alone when the box is emptied.
        nickname: nickname.trim() || null,
      },
      { onSuccess: close },
    );
  };

  return (
    <Modal open={entry !== null} title="Edit chemical" onClose={close}>
      <ModalForm onSubmit={submit}>
        <ModalTitle>Edit chemical</ModalTitle>

        <ModalField>
          <ModalLabel>Chemical id</ModalLabel>
          <ModalInput
            value={chemicalId}
            onChange={(e) => setChemicalId(e.target.value)}
            required
            autoFocus
            maxLength={60}
            placeholder="e.g. CHEBI:16236"
          />
        </ModalField>

        <ModalField>
          <ModalLabel>Nickname</ModalLabel>
          <ModalInput
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            maxLength={60}
            placeholder="What your group calls it, e.g. BPA stock"
          />
        </ModalField>

        {updateChemical.error && (
          <ModalText role="alert">{updateChemical.error.message}</ModalText>
        )}

        <ModalActions>
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
        </ModalActions>
      </ModalForm>
    </Modal>
  );
};

export default EditChemicalForm;
