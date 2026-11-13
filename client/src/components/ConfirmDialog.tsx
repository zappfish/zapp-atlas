import Modal from "./Modal";
import {
  ModalActions,
  ModalPanel,
  ModalText,
  ModalTitle,
} from "@/styles/elements";

/** Confirmation before something irreversible. */
const ConfirmDialog = ({
  open,
  title,
  message,
  confirmLabel = "Remove",
  isPending = false,
  error,
  onConfirm,
  onClose,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  isPending?: boolean;
  error?: string;
  onConfirm: () => void;
  onClose: () => void;
}) => (
  <Modal open={open} title={title} onClose={onClose}>
    <ModalPanel>
      <ModalTitle>{title}</ModalTitle>
      <ModalText>{message}</ModalText>

      {error && (
<ModalText role="alert">{error}</ModalText>
      )}

      <ModalActions>
        <button className="btn btn--neutral" type="button" onClick={onClose}>
          Cancel
        </button>
        <button
          className="btn btn--danger"
          type="button"
          onClick={onConfirm}
          disabled={isPending}
        >
          {isPending ? "Removing…" : confirmLabel}
        </button>
      </ModalActions>
    </ModalPanel>
  </Modal>
);

export default ConfirmDialog;
