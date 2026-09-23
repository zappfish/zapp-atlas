import Modal from "./Modal";

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
    <div className="modal__panel">
      <h2 className="modal__title">{title}</h2>
      <p className="modal__text">{message}</p>

      {error && (
        <p className="modal__text" role="alert">
          {error}
        </p>
      )}

      <div className="modal__actions">
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
      </div>
    </div>
  </Modal>
);

export default ConfirmDialog;
