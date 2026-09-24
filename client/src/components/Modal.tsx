import { useEffect, useRef, type ReactNode } from "react";

/**
 * A dialog built on <dialog>, so Escape, focus trapping and the backdrop come
 * from the element rather than from us. Styles are .modal in components.css.
 */
const Modal = ({
  open,
  title,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}) => {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    // showModal() is what makes it modal; the open attribute alone does not.
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      className="modal"
      ref={ref}
      aria-label={title}
      // Fires on Escape as well as close(), so the parent's state keeps up.
      onClose={onClose}
    >
      {open && children}
    </dialog>
  );
};

export default Modal;
