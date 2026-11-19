import Modal from "./Modal";
import {
  ModalActions,
  ModalPanel,
  ModalText,
  ModalTitle,
} from "@/styles/elements";

/** Confirmation before something that matters. A removal, unless told otherwise. */
const ConfirmDialog = ({
  open,
  title,
  message,
  confirmLabel = "Remove",
  pendingLabel = "Removing…",
  danger = true,
  isPending = false,
  error,
  onConfirm,
  onClose,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  pendingLabel?: string;
  danger?: boolean;
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
          className={danger ? "btn btn--danger" : "btn btn--primary"}
          type="button"
          onClick={onConfirm}
          disabled={isPending}
        >
          {isPending ? pendingLabel : confirmLabel}
        </button>
      </ModalActions>
    </ModalPanel>
  </Modal>
);

export default ConfirmDialog;
