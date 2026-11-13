import { useEffect, useRef, type ReactNode } from "react";

/**
 * Built on <dialog>, so Escape, focus trapping and the backdrop come from the
 * element. Styles are .modal in components.css.
 */
const Modal = ({
  open,
  title,
  onClose,
  isWide = false,
  isLarge = false,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  /** For one holding a list as well as its fields. */
  isWide?: boolean;
  /** Near full screen, for a picker with panes of its own. */
  isLarge?: boolean;
  children: ReactNode;
}) => {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    // showModal() is what makes it modal; the open attribute does not.
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      className={
        isLarge ? "modal modal--large" : isWide ? "modal modal--wide" : "modal"
      }
      ref={ref}
      aria-label={title}
      // Fires on Escape too, so the parent's state keeps up.
      onClose={onClose}
    >
      {open && children}
    </dialog>
  );
};

export default Modal;
